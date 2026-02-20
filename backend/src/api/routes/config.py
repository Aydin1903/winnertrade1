"""
Config API – config oku/yaz, bağlantı testi.
GUI Settings ekranı bu endpoint'leri kullanır.
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from core.config_schema import AppConfig
from storage.config_storage import ConfigStorage
from core.paths import get_config_path

router = APIRouter()

# API yanıtında api_secret maskelenir
MASK = "********"


def _mask_secret(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    out = config_dict.copy()
    if "exchange" in out and isinstance(out["exchange"], dict):
        ex = out["exchange"].copy()
        if ex.get("api_secret"):
            ex["api_secret"] = MASK
        out["exchange"] = ex
    return out


@router.get("/config")
def get_config() -> dict:
    """
    Mevcut config'i döndürür. api_secret maskelenir.
    Config yoksa 404.
    """
    storage = ConfigStorage()
    if not storage.exists():
        raise HTTPException(
            status_code=404,
            detail="Config dosyası bulunamadı. İlk kurulumda Setup ekranından ayarları yapın.",
        )
    try:
        cfg = storage.load()
        return _mask_secret(cfg.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Config okunamadı: {e}")


@router.put("/config")
def put_config(body: dict) -> dict:
    """
    Config günceller. Body Pydantic şemasına uymalı.
    api_secret gönderilmezse veya maskeli (********) ise mevcut değer korunur.
    """
    storage = ConfigStorage()
    # Mevcut config'i al; secret maskeli gelirse değiştirme
    if storage.exists():
        try:
            current = storage.load().model_dump()
            if body.get("exchange") and isinstance(body["exchange"], dict):
                new_secret = body["exchange"].get("api_secret")
                if new_secret in (None, "", MASK):
                    body["exchange"] = {**body["exchange"], "api_secret": current["exchange"].get("api_secret", "")}
        except Exception:
            pass
    try:
        config = AppConfig.model_validate(body)
        storage.save(config)
        return _mask_secret(config.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Config geçersiz: {e}")


@router.post("/config/test-connection")
def test_connection(body: dict) -> dict:
    """
    Verilen config ile exchange bağlantısını dener (bakiye sorgusu).
    Body tam config veya sadece exchange/account blokları olabilir; şema doğrulanır.
    """
    from exchanges.factory import get_exchange_from_config_dict

    try:
        config = AppConfig.model_validate(body)
        cfg_dict = config.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Config geçersiz: {e}")

    try:
        exchange = get_exchange_from_config_dict(cfg_dict)
        balance = exchange.get_balance()
        return {"ok": True, "message": "Bağlantı başarılı.", "balance": balance}
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Bağlantı testi başarısız: {str(e)}",
        )


@router.get("/config/path")
def get_config_path_info() -> dict:
    """Config dosyasının kullanılan yolunu döndürür (GUI'de göstermek için)."""
    return {"config_path": str(get_config_path())}
