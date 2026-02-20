"""
Trading Engine Loop - Sinyal kontrolü, pozisyon açma, trailing, kapatma, istatistik.

Tek process olarak çalıştırılır (örn. python -m engine veya scripts/run_engine.py).
GUI (API) ayrı process'tir; engine bakiye/pozisyonu exchange üzerinden günceller, API aynı config ile okuyabilir.
"""

import time
from typing import Any, Dict, List

try:
    from core.config_manager import ConfigManager
    from core.state import AppState
    from exchanges.factory import get_exchange
    from strategy import get_daily_trend, get_entry_signal, get_atr_and_stop_price
    from strategy.indicators import ohlcv_to_dataframe, compute_atr
    from risk import RiskManager, can_open_trade, stop_distance_price
    from execution import open_position, close_position, create_trailing_state
    from stats import record_trade, log_trade_event, log_signal, log_trailing
    from utils.telegram import notify_trade_opened, notify_trade_closed, notify_daily_limit
except ImportError:
    from ..core.config_manager import ConfigManager
    from ..core.state import AppState
    from ..exchanges.factory import get_exchange
    from ..strategy import get_daily_trend, get_entry_signal, get_atr_and_stop_price
    from ..strategy.indicators import ohlcv_to_dataframe, compute_atr
    from ..risk import RiskManager, can_open_trade, stop_distance_price
    from ..execution import open_position, close_position, create_trailing_state
    from ..stats import record_trade, log_trade_event, log_signal, log_trailing
    from ..utils.telegram import notify_trade_opened, notify_trade_closed, notify_daily_limit


def _get_top_symbols_from_exchange(exchange, limit: int = 10) -> List[str]:
    """Exchange'den hacme göre en yüksek USDT perpetual sembollerini döndürür. ccxt _client gerekir."""
    try:
        client = getattr(exchange, "_client", None) or getattr(exchange, "_data", None)
        if client is None:
            return []
        tickers = client.fetch_tickers()
        out = []
        for sym, t in tickers.items():
            if "/USDT" not in str(sym) and "USDT" not in str(sym).upper():
                continue
            if "USDT:USDT" in str(sym) or ":USDT" not in str(sym):
                if str(sym).endswith("USDT") or "/USDT" in str(sym):
                    pass
                else:
                    continue
            quote_vol = float(t.get("quoteVolume") or t.get("info", {}).get("quoteVolume") or 0)
            if quote_vol <= 0:
                continue
            out.append((sym, quote_vol))
        out.sort(key=lambda x: -x[1])
        return [s for s, _ in out[:limit]]
    except Exception:
        return []


def _get_symbols(exchange=None) -> List[str]:
    config = ConfigManager()
    manual = config.get("symbols.manual_list") or []
    if isinstance(manual, list) and len(manual) > 0:
        return [str(s) for s in manual]
    if config.get("symbols.auto_detect_top_10") and exchange is not None:
        top = _get_top_symbols_from_exchange(exchange, limit=10)
        if top:
            return top
    return ["BTC/USDT"]


def _get_current_atr(exchange, symbol: str, timeframe: str = "15m", period: int = 14) -> float:
    """Son kapanan mumun ATR değeri."""
    try:
        ohlcv = exchange.get_klines(symbol, timeframe, limit=period + 20)
        if not ohlcv or len(ohlcv) < period:
            return 0.0
        df = ohlcv_to_dataframe(ohlcv)
        atr_series = compute_atr(df["high"], df["low"], df["close"], period)
        last = atr_series.iloc[-1]
        return float(last) if last and last == last else 0.0  # NaN check
    except Exception:
        return 0.0


def _run_once(
    exchange,
    state: AppState,
    risk_manager: RiskManager,
    symbols: List[str],
    tracked: Dict[str, Dict[str, Any]],
) -> None:
    config = ConfigManager()
    timeframe = config.get("strategy.timeframe") or "15m"

    # 1) Açık pozisyonları kontrol et: trailing veya kapat
    for symbol in list(tracked.keys()):
        pos = tracked[symbol]
        try:
            ticker = exchange.get_ticker(symbol)
            mark = float(ticker.get("last") or 0)
            if mark <= 0:
                continue
            atr = _get_current_atr(exchange, symbol, timeframe)
            if atr <= 0:
                atr = abs(pos["entry_price"] - pos["stop_price"])  # fallback
            should_close, new_stop = pos["trailing_state"].update(mark, atr)
            if should_close:
                close_position(exchange, symbol, pos["side"], pos["quantity"])
                exit_price = mark
                if pos["side"] == "long":
                    pnl = (exit_price - pos["entry_price"]) * pos["quantity"]
                else:
                    pnl = (pos["entry_price"] - exit_price) * pos["quantity"]
                r = RiskManager.pnl_to_r(pnl, pos["risk_amount"])
                state.add_day_r(r)
                record_trade(pnl, r, 0.0)
                log_trade_event(
                    symbol, pos["side"], pos["entry_price"], exit_price,
                    pos["quantity"], pnl, r, 0.0,
                )
                log_trailing(symbol, pos["side"], mark, new_stop, "close")
                try:
                    notify_trade_closed(symbol, pos["side"], pnl, r)
                    if state.trading_disabled_today:
                        notify_daily_limit(state.get_day_r())
                except Exception:
                    pass
                del tracked[symbol]
        except Exception as e:
            # Log and keep position
            pass

    # 2) Yeni sinyal: açık pozisyon yoksa ve limit yoksa sinyal ara ve aç
    if not can_open_trade(state):
        return
    for symbol in symbols:
        if symbol in tracked:
            continue
        try:
            signal = get_entry_signal(symbol, exchange)
            if not signal:
                continue
            atr_val, stop_price, entry_price = get_atr_and_stop_price(symbol, exchange, signal)
            if not stop_price or not entry_price or stop_price <= 0 or entry_price <= 0:
                continue
            stop_dist = stop_distance_price(entry_price, stop_price)
            quantity = risk_manager.get_position_size(stop_dist)
            if quantity <= 0:
                continue
            quantity = round(quantity, 6)
            order = open_position(exchange, symbol, signal, quantity)
            filled = float(order.get("filled") or 0)
            avg_price = order.get("avg_price")
            if filled <= 0:
                continue
            avg_price = float(avg_price) if avg_price is not None else entry_price
            risk_amount = risk_manager.get_risk_amount()
            trailing_state = create_trailing_state(
                symbol, signal, avg_price, stop_price, filled
            )
            tracked[symbol] = {
                "side": signal,
                "quantity": filled,
                "entry_price": avg_price,
                "stop_price": stop_price,
                "risk_amount": risk_amount,
                "trailing_state": trailing_state,
            }
            log_signal(symbol, signal, "opened")
            try:
                notify_trade_opened(symbol, signal, filled, avg_price)
            except Exception:
                pass
        except Exception as e:
            pass


def run_engine(interval_seconds: int = 60, stop_event=None) -> None:
    """
    Engine döngüsünü başlatır.
    interval_seconds: sinyal ve trailing kontrol aralığı (saniye).
    stop_event: threading.Event; set edilirse döngü biter. None ise sonsuz döngü.
    """
    exchange = get_exchange()
    state = AppState()
    risk_manager = RiskManager()
    symbols = _get_symbols(exchange)
    tracked: Dict[str, Dict[str, Any]] = {}

    while True:
        if stop_event is not None and stop_event.is_set():
            break
        try:
            _run_once(exchange, state, risk_manager, symbols, tracked)
        except Exception as e:
            pass
        if stop_event is not None:
            if stop_event.wait(timeout=interval_seconds):
                break
        else:
            time.sleep(interval_seconds)
