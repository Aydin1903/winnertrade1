"""
İndikatörler - EMA, MACD, RSI, ATR (pandas/numpy, ta-lib bağımlılığı yok).

Girdi: get_klines formatı [timestamp, open, high, low, close, volume] listesi
veya (open, high, low, close) array'leri.
"""

from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd


def _to_series(ohlcv: List[List], key: str) -> pd.Series:
    """OHLCV listesinden tek sütun Series. key: 'open','high','low','close','volume'."""
    idx = {"open": 1, "high": 2, "low": 3, "close": 4, "volume": 5}[key]
    return pd.Series([row[idx] for row in ohlcv], dtype=float)


def ohlcv_to_dataframe(ohlcv: List[List]) -> pd.DataFrame:
    """ccxt OHLCV listesini DataFrame'e çevirir."""
    if not ohlcv:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    df = pd.DataFrame(
        ohlcv,
        columns=["timestamp", "open", "high", "low", "close", "volume"],
    )
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def compute_ema(close: Union[pd.Series, List[float]], period: int) -> pd.Series:
    """EMA(period). close: kapanış fiyatları."""
    if isinstance(close, list):
        close = pd.Series(close)
    return close.ewm(span=period, adjust=False).mean()


def compute_macd(
    close: Union[pd.Series, List[float]],
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    MACD line, signal line, histogram.
    Returns: (macd_line, signal_line, histogram)
    """
    if isinstance(close, list):
        close = pd.Series(close)
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def compute_rsi(close: Union[pd.Series, List[float]], period: int = 14) -> pd.Series:
    """RSI(period)."""
    if isinstance(close, list):
        close = pd.Series(close)
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.ewm(span=period, adjust=False).mean()
    avg_loss = loss.ewm(span=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_atr(
    high: Union[pd.Series, List[float]],
    low: Union[pd.Series, List[float]],
    close: Union[pd.Series, List[float]],
    period: int = 14,
) -> pd.Series:
    """ATR(period)."""
    if isinstance(high, list):
        high, low, close = pd.Series(high), pd.Series(low), pd.Series(close)
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.ewm(span=period, adjust=False).mean()


def add_indicators_to_df(
    df: pd.DataFrame,
    ema_period: int = 200,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    rsi_period: int = 14,
    atr_period: int = 14,
) -> pd.DataFrame:
    """
    DataFrame'e EMA, MACD, RSI, ATR ekler (sütunlar: ema, macd, signal, macd_hist, rsi, atr).
    """
    c, h, l = df["close"], df["high"], df["low"]
    df = df.copy()
    df["ema"] = compute_ema(c, ema_period)
    macd_line, signal_line, hist = compute_macd(c, macd_fast, macd_slow, macd_signal)
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["macd_hist"] = hist
    df["rsi"] = compute_rsi(c, rsi_period)
    df["atr"] = compute_atr(h, l, c, atr_period)
    return df
