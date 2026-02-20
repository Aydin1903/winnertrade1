"""
Trade / Signals / Trailing log - Günlük dosyalara yazar.

Dosyalar: logs/trades_YYYY-MM-DD.log, signals_YYYY-MM-DD.log, trailing_YYYY-MM-DD.log
Config: logging.log_dir (örn. backend/logs)
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from ..core.config_manager import ConfigManager
except ImportError:
    from core.config_manager import ConfigManager


def _log_dir() -> Path:
    backend = Path(__file__).resolve().parent.parent.parent
    config = ConfigManager()
    raw = config.get("logging.log_dir") or "logs"
    p = Path(raw)
    if not p.is_absolute():
        p = backend / (raw.replace("backend/", "").strip("/") or "logs")
    p.mkdir(parents=True, exist_ok=True)
    return p


def _line(prefix: str, payload: Dict[str, Any]) -> str:
    parts = [f"[{datetime.now().isoformat()}]", prefix]
    for k, v in payload.items():
        parts.append(f"{k}={v}")
    return " ".join(str(x) for x in parts) + "\n"


def log_trade(
    symbol: str,
    side: str,
    entry_price: float,
    exit_price: float,
    quantity: float,
    pnl_usdt: float,
    r_value: float,
    fees: float = 0.0,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Tek bir kapanan trade'i trades_YYYY-MM-DD.log'a yazar."""
    d = _log_dir()
    today = datetime.now().strftime("%Y-%m-%d")
    path = d / f"trades_{today}.log"
    payload = {
        "symbol": symbol,
        "side": side,
        "entry": entry_price,
        "exit": exit_price,
        "qty": quantity,
        "pnl": round(pnl_usdt, 2),
        "r": round(r_value, 2),
        "fees": round(fees, 4),
    }
    if extra:
        payload.update(extra)
    with open(path, "a", encoding="utf-8") as f:
        f.write(_line("TRADE", payload))


def log_signal(
    symbol: str,
    direction: str,
    reason: str = "",
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Sinyal logu: signals_YYYY-MM-DD.log."""
    d = _log_dir()
    today = datetime.now().strftime("%Y-%m-%d")
    path = d / f"signals_{today}.log"
    payload = {"symbol": symbol, "direction": direction, "reason": reason or "entry"}
    if extra:
        payload.update(extra)
    with open(path, "a", encoding="utf-8") as f:
        f.write(_line("SIGNAL", payload))


def log_trailing(
    symbol: str,
    side: str,
    mark_price: float,
    current_stop: float,
    action: str,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Trailing stop güncellemesi: trailing_YYYY-MM-DD.log. action: break_even | trailing | close."""
    d = _log_dir()
    today = datetime.now().strftime("%Y-%m-%d")
    path = d / f"trailing_{today}.log"
    payload = {
        "symbol": symbol,
        "side": side,
        "mark": mark_price,
        "stop": current_stop,
        "action": action,
    }
    if extra:
        payload.update(extra)
    with open(path, "a", encoding="utf-8") as f:
        f.write(_line("TRAIL", payload))
