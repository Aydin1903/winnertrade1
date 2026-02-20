"""
Telegram bildirimleri - Trade açıldı/kapandı, günlük -3R uyarısı.

Config: telegram.enabled, telegram.bot_token, telegram.chat_id
Yoksa veya enabled false ise sessizce atlanır.
"""

from typing import Optional

try:
    from ..core.config_manager import ConfigManager
except ImportError:
    from core.config_manager import ConfigManager

import httpx


def _is_enabled() -> bool:
    config = ConfigManager()
    return bool(config.get("telegram.enabled") and config.get("telegram.bot_token") and config.get("telegram.chat_id"))


def _send(text: str) -> bool:
    if not _is_enabled():
        return False
    try:
        config = ConfigManager()
        token = config.get("telegram.bot_token", "").strip()
        chat_id = str(config.get("telegram.chat_id", "")).strip()
        if not token or not chat_id:
            return False
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        with httpx.Client(timeout=10.0) as client:
            r = client.post(url, json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True})
            return r.is_success
    except Exception:
        return False


def send_telegram(text: str) -> bool:
    """Serbest metin gönderir. Config yoksa False döner."""
    return _send(text)


def notify_trade_opened(symbol: str, side: str, quantity: float, entry_price: float) -> bool:
    """Pozisyon açıldı bildirimi."""
    return _send(
        f"🟢 Trade açıldı\n{symbol} {side.upper()}\nMiktar: {quantity}\nGiriş: {entry_price}"
    )


def notify_trade_closed(symbol: str, side: str, pnl: float, r: float) -> bool:
    """Pozisyon kapandı bildirimi."""
    emoji = "✅" if pnl >= 0 else "❌"
    return _send(
        f"{emoji} Trade kapandı\n{symbol} {side.upper()}\nPnL: {pnl:.2f} USDT | R: {r:.2f}"
    )


def notify_daily_limit(day_r: float) -> bool:
    """Günlük -3R limitine ulaşıldı uyarısı."""
    return _send(
        f"⛔ Günlük limit\nTrading bugün durduruldu.\nDay R: {day_r:.2f}"
    )
