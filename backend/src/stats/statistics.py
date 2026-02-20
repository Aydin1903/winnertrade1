"""
İstatistik modülü - total/day PnL, R, win rate, fees, trading_disabled_today.

Veriler backend/data/stats.json içinde saklanır.
day_r ve trading_disabled_today state'ten alınır; diğerleri burada güncellenir.
"""

from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from ..core.config_manager import ConfigManager
except ImportError:
    from core.config_manager import ConfigManager


def _stats_path() -> Path:
    config = ConfigManager()
    base = Path(__file__).resolve().parent.parent.parent  # backend
    data_dir = base / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "stats.json"


def _load() -> Dict[str, Any]:
    p = _stats_path()
    if not p.exists():
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "total_pnl": 0.0,
            "total_fees": 0.0,
            "total_r": 0.0,
            "max_win": 0.0,
            "max_loss": 0.0,
            "max_r": 0.0,
            "min_r": 0.0,
            "daily": [],  # [{"date": "YYYY-MM-DD", "pnl": float, "r": float, "fees": float}, ...]
        }
    import json
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "daily" not in data:
        data["daily"] = []
    return data


def _save(data: Dict[str, Any]) -> None:
    import json
    with open(_stats_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def record_trade(
    pnl_usdt: float,
    r_value: float,
    fees: float = 0.0,
) -> None:
    """
    Kapanan bir trade'i kaydet; toplam ve günlük istatistikleri günceller.
    """
    data = _load()
    today = date.today().isoformat()

    data["total_trades"] = data.get("total_trades", 0) + 1
    data["total_pnl"] = data.get("total_pnl", 0) + pnl_usdt
    data["total_fees"] = data.get("total_fees", 0) + fees
    data["total_r"] = data.get("total_r", 0) + r_value

    if pnl_usdt > 0:
        data["wins"] = data.get("wins", 0) + 1
        data["max_win"] = max(data.get("max_win", 0), pnl_usdt)
    else:
        data["losses"] = data.get("losses", 0) + 1
        data["max_loss"] = min(data.get("max_loss", 0), pnl_usdt)

    if r_value > data.get("max_r", 0):
        data["max_r"] = r_value
    if data.get("min_r", 0) == 0 or r_value < data["min_r"]:
        data["min_r"] = r_value

    daily = data.get("daily", [])
    found = False
    for d in daily:
        if d.get("date") == today:
            d["pnl"] = d.get("pnl", 0) + pnl_usdt
            d["r"] = d.get("r", 0) + r_value
            d["fees"] = d.get("fees", 0) + fees
            found = True
            break
    if not found:
        daily.append({"date": today, "pnl": pnl_usdt, "r": r_value, "fees": fees})
    data["daily"] = daily

    _save(data)


def get_day_pnl() -> float:
    """Bugünkü PnL (kayıtlı trade'lerden)."""
    data = _load()
    today = date.today().isoformat()
    for d in data.get("daily", []):
        if d.get("date") == today:
            return float(d.get("pnl", 0))
    return 0.0


def get_day_fees() -> float:
    """Bugünkü fees."""
    data = _load()
    today = date.today().isoformat()
    for d in data.get("daily", []):
        if d.get("date") == today:
            return float(d.get("fees", 0))
    return 0.0


def get_snapshot(state=None) -> Dict[str, Any]:
    """
    GUI/API için tüm istatistikleri döndürür.
    state verilirse day_r ve trading_disabled_today state'ten alınır.
    """
    data = _load()
    total_trades = data.get("total_trades", 0)
    wins = data.get("wins", 0)
    losses = data.get("losses", 0)
    total_pnl = float(data.get("total_pnl", 0))
    total_fees = float(data.get("total_fees", 0))
    total_r = float(data.get("total_r", 0))
    max_win = float(data.get("max_win", 0))
    max_loss = float(data.get("max_loss", 0))
    max_r = float(data.get("max_r", 0))
    min_r = float(data.get("min_r", 0))

    day_pnl = get_day_pnl()
    day_fees = get_day_fees()
    day_r = 0.0
    trading_disabled_today = False
    if state is not None:
        state.reset_daily()
        day_r = state.get_day_r()
        trading_disabled_today = state.trading_disabled_today

    win_rate = (wins / total_trades * 100) if total_trades else 0
    avg_pnl = (total_pnl / total_trades) if total_trades else 0
    avg_r = (total_r / total_trades) if total_trades else 0

    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "total_pnl": total_pnl,
        "day_pnl": day_pnl,
        "win_rate": round(win_rate, 2),
        "avg_pnl": round(avg_pnl, 2),
        "max_win": max_win,
        "max_loss": max_loss,
        "total_r": round(total_r, 2),
        "day_r": round(day_r, 2),
        "avg_r": round(avg_r, 2),
        "max_r": round(max_r, 2),
        "min_r": round(min_r, 2),
        "total_fees": total_fees,
        "day_fees": day_fees,
        "trading_disabled_today": trading_disabled_today,
    }
