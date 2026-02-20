"""
Engine kontrol API - start / stop / status.
Engine aynı process içinde background thread'de çalışır.
"""

import threading
from typing import Optional

from fastapi import APIRouter, HTTPException

router = APIRouter()

_engine_thread: Optional[threading.Thread] = None
_engine_stop_event: Optional[threading.Event] = None
_engine_interval: int = 60


def _run_engine_thread() -> None:
    global _engine_stop_event
    from engine.loop import run_engine
    run_engine(interval_seconds=_engine_interval, stop_event=_engine_stop_event)


@router.post("/engine/start")
def engine_start(interval_seconds: int = 60) -> dict:
    """Trading engine'i arka planda başlatır. Zaten çalışıyorsa 409."""
    global _engine_thread, _engine_stop_event, _engine_interval
    if _engine_thread is not None and _engine_thread.is_alive():
        raise HTTPException(status_code=409, detail="Engine already running")
    _engine_interval = max(30, min(300, int(interval_seconds)))
    _engine_stop_event = threading.Event()
    _engine_thread = threading.Thread(target=_run_engine_thread, daemon=True)
    _engine_thread.start()
    return {"status": "started", "interval_seconds": _engine_interval}


@router.post("/engine/stop")
def engine_stop() -> dict:
    """Trading engine'i durdurur."""
    global _engine_thread, _engine_stop_event
    if _engine_stop_event is None:
        return {"status": "stopped", "message": "was not running"}
    _engine_stop_event.set()
    if _engine_thread is not None:
        _engine_thread.join(timeout=15)
    _engine_thread = None
    _engine_stop_event = None
    return {"status": "stopped"}


@router.get("/engine/status")
def engine_status() -> dict:
    """Engine çalışıyor mu?"""
    running = _engine_thread is not None and _engine_thread.is_alive()
    return {"running": running, "interval_seconds": _engine_interval if running else None}
