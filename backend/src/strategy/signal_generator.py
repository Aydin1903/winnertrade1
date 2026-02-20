"""
15m Entry Sinyal Üretici - Günlük trend + 15m EMA/MACD/RSI ile long/short sinyali.

Kurallar:
  LONG:  (günlük long veya neutral) + 15m fiyat > EMA200 + MACD > Signal + RSI > 50
  SHORT: (günlük short veya neutral) + 15m fiyat < EMA200 + MACD < Signal + RSI < 50

MACD "kesişim" için: son bar'da MACD > Signal (long) veya MACD < Signal (short)
ve bir önceki bar'da tersi (momentum dönüşü) isteğe bağlı; basit haliyle son bar koşulu yeterli.
"""

from typing import Literal, Optional

import pandas as pd

try:
    from ..core.config_manager import ConfigManager
except ImportError:
    from core.config_manager import ConfigManager

from .indicators import add_indicators_to_df, ohlcv_to_dataframe
from .trend_filter import TrendDirection, get_daily_trend

SignalDirection = Literal["long", "short"]


def get_entry_signal(
    symbol: str,
    exchange,
    daily_trend: Optional[TrendDirection] = None,
    timeframe: Optional[str] = None,
    limit: int = 250,
) -> Optional[SignalDirection]:
    """
    15m grafikte entry sinyali: long, short veya None.

    Args:
        symbol: Sembol (exchange formatında)
        exchange: BaseExchange
        daily_trend: None ise get_daily_trend ile hesaplanır
        timeframe: None ise config'ten 15m
        limit: 15m mum sayısı

    Returns:
        "long" | "short" | None
    """
    config = ConfigManager()
    if timeframe is None:
        timeframe = config.get("strategy.timeframe") or "15m"
    if daily_trend is None:
        daily_trend = get_daily_trend(symbol, exchange)

    ema_period = int(config.get("strategy.entry.ema_period") or 200)
    macd_fast = int(config.get("strategy.entry.macd_fast") or 12)
    macd_slow = int(config.get("strategy.entry.macd_slow") or 26)
    macd_signal = int(config.get("strategy.entry.macd_signal") or 9)
    rsi_period = int(config.get("strategy.entry.rsi_period") or 14)
    rsi_threshold = float(config.get("strategy.entry.rsi_threshold") or 50)

    ohlcv = exchange.get_klines(symbol, timeframe, limit=limit)
    if not ohlcv or len(ohlcv) < ema_period:
        return None

    df = ohlcv_to_dataframe(ohlcv)
    df = add_indicators_to_df(
        df,
        ema_period=ema_period,
        macd_fast=macd_fast,
        macd_slow=macd_slow,
        macd_signal=macd_signal,
        rsi_period=rsi_period,
        atr_period=14,
    )

    last = df.iloc[-1]
    close = last["close"]
    ema = last["ema"]
    macd = last["macd"]
    sig = last["macd_signal"]
    rsi = last["rsi"]

    if any(pd.isna(x) for x in [ema, macd, sig, rsi]):
        return None

    # LONG: günlük long veya neutral; 15m fiyat > EMA, MACD > Signal, RSI > 50
    if daily_trend in ("long", "neutral"):
        if close > ema and macd > sig and rsi > rsi_threshold:
            return "long"

    # SHORT: günlük short veya neutral; 15m fiyat < EMA, MACD < Signal, RSI < 50
    if daily_trend in ("short", "neutral"):
        if close < ema and macd < sig and rsi < rsi_threshold:
            return "short"

    return None


def get_atr_and_stop_price(
    symbol: str,
    exchange,
    side: SignalDirection,
    atr_multiplier: Optional[float] = None,
    timeframe: Optional[str] = None,
    limit: int = 50,
) -> tuple:
    """
    Stop mesafesi (ATR * multiplier) ve stop fiyatı.
    Long: stop = entry - atr * mult; Short: stop = entry + atr * mult.
    Entry olarak son kapanış veya mevcut fiyat kullanılabilir; burada son close kullanıyoruz.

    Returns:
        (atr_value, stop_price, entry_price)
    """
    config = ConfigManager()
    if timeframe is None:
        timeframe = config.get("strategy.timeframe") or "15m"
    if atr_multiplier is None:
        atr_multiplier = float(config.get("strategy.stop.atr_multiplier") or 1.5)
    atr_period = int(config.get("strategy.stop.atr_period") or 14)

    ohlcv = exchange.get_klines(symbol, timeframe, limit=limit)
    if not ohlcv or len(ohlcv) < atr_period:
        return 0.0, 0.0, 0.0

    df = ohlcv_to_dataframe(ohlcv)
    from .indicators import compute_atr

    df["atr"] = compute_atr(df["high"], df["low"], df["close"], atr_period)
    last = df.iloc[-1]
    entry_price = float(last["close"])
    atr_value = float(last["atr"])
    if pd.isna(atr_value) or atr_value <= 0:
        return 0.0, 0.0, entry_price

    distance = atr_value * atr_multiplier
    if side == "long":
        stop_price = entry_price - distance
    else:
        stop_price = entry_price + distance

    return atr_value, stop_price, entry_price
