"""
1D Trend Filtresi - Günlük grafikte yön: LONG / SHORT / NEUTRAL.

Kurallar:
  Fiyat > EMA200 ve MACD > Signal  → LONG (sadece long bak)
  Fiyat < EMA200 ve MACD < Signal → SHORT (sadece short bak)
  Aksi halde                      → NEUTRAL (15m hangi yöne sinyal verirse o yönde açılabilir)
"""

from typing import Literal, Optional

import pandas as pd

try:
    from ..core.config_manager import ConfigManager
except ImportError:
    from core.config_manager import ConfigManager

from .indicators import add_indicators_to_df, ohlcv_to_dataframe

TrendDirection = Literal["long", "short", "neutral"]


def get_daily_trend(
    symbol: str,
    exchange,
    timeframe: Optional[str] = None,
    limit: int = 300,
) -> TrendDirection:
    """
    Günlük (1d) grafiğe göre trend yönü döndürür.

    Args:
        symbol: Örn. BTC/USDT veya BTCUSDT (exchange formatına uygun)
        exchange: BaseExchange (get_klines kullanır)
        timeframe: None ise config'ten strategy.trend_filter.timeframe (1d)
        limit: Kaç mum çekilecek (EMA200 için en az 200+)

    Returns:
        "long" | "short" | "neutral"
    """
    config = ConfigManager()
    if timeframe is None:
        timeframe = config.get("strategy.trend_filter.timeframe") or "1d"
    ema_period = int(config.get("strategy.trend_filter.ema_period") or 200)
    macd_fast = int(config.get("strategy.trend_filter.macd_fast") or 12)
    macd_slow = int(config.get("strategy.trend_filter.macd_slow") or 26)
    macd_signal = int(config.get("strategy.trend_filter.macd_signal") or 9)

    ohlcv = exchange.get_klines(symbol, timeframe, limit=limit)
    if not ohlcv or len(ohlcv) < ema_period:
        return "neutral"

    df = ohlcv_to_dataframe(ohlcv)
    df = add_indicators_to_df(
        df,
        ema_period=ema_period,
        macd_fast=macd_fast,
        macd_slow=macd_slow,
        macd_signal=macd_signal,
        rsi_period=14,
        atr_period=14,
    )

    # Son kapanan mum (son tamamlanmış bar)
    last = df.iloc[-1]
    close = last["close"]
    ema = last["ema"]
    macd = last["macd"]
    sig = last["macd_signal"]

    if pd.isna(ema) or pd.isna(macd) or pd.isna(sig):
        return "neutral"

    if close > ema and macd > sig:
        return "long"
    if close < ema and macd < sig:
        return "short"
    return "neutral"
