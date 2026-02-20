"""
Dashboard API - stats, positions, ticker, logs.
"""

from datetime import date
from pathlib import Path
from typing import Any, List, Optional

from fastapi import APIRouter, HTTPException

router = APIRouter()

# Lazy singletons (config/exchange/state ilk istekte yüklenir)
_exchange = None
_state = None


def _get_exchange():
    global _exchange
    if _exchange is None:
        try:
            from exchanges.factory import get_exchange
            _exchange = get_exchange()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Exchange init failed: {e}")
    return _exchange


def _get_state():
    global _state
    if _state is None:
        try:
            from core.state import AppState
            _state = AppState()
        except Exception:
            _state = None
    return _state


@router.get("/stats")
def get_stats() -> dict:
    """İstatistik snapshot (get_snapshot)."""
    try:
        from stats.statistics import get_snapshot
        state = _get_state()
        return get_snapshot(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions")
def get_positions(symbol: Optional[str] = None) -> List[dict]:
    """Açık pozisyonlar."""
    try:
        ex = _get_exchange()
        return ex.get_positions(symbol)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ticker")
def get_ticker(symbol: str = "BTC/USDT") -> dict:
    """Son fiyat (last, bid, ask)."""
    try:
        ex = _get_exchange()
        return ex.get_ticker(symbol)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _read_log_lines(log_name: str, limit: int = 100) -> List[str]:
    """logs/{log_name}_YYYY-MM-DD.log son limit satır."""
    try:
        from stats.trade_logger import _log_dir
        d = _log_dir()
        today = date.today().isoformat()
        path = d / f"{log_name}_{today}.log"
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        return lines[-limit:] if len(lines) > limit else lines
    except Exception:
        return []


@router.get("/logs/trades")
def get_trades_log(limit: int = 100) -> List[str]:
    return _read_log_lines("trades", limit)


@router.get("/logs/signals")
def get_signals_log(limit: int = 100) -> List[str]:
    return _read_log_lines("signals", limit)


@router.get("/logs/trailing")
def get_trailing_log(limit: int = 100) -> List[str]:
    return _read_log_lines("trailing", limit)


@router.get("/last_signal")
def get_last_signal() -> dict:
    """Son sinyal (signals log son satırından)."""
    lines = _read_log_lines("signals", limit=1)
    if not lines:
        return {"direction": None, "symbol": None, "raw": None}
    return {"raw": lines[-1], "direction": None, "symbol": None}


@router.get("/balance")
def get_balance() -> dict:
    try:
        ex = _get_exchange()
        return {"balance": ex.get_balance()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
