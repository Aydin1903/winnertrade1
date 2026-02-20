"""
Exchange Factory - Config'e göre doğru exchange instance döndürür.

Kullanım:
    from exchanges.factory import get_exchange
    
    exchange = get_exchange()
    # veya config path ile:
    exchange = get_exchange(config_path="path/to/config.json")
"""

from pathlib import Path
from typing import Any, Dict, Optional

from .base_exchange import BaseExchange
from .binance_futures import BinanceFuturesExchange
from .mexc_futures import MEXCFuturesExchange
from .paper_trader import PaperTrader


def _get(key: str, data: Dict[str, Any], default: Any = None) -> Any:
    """Nokta notasyonu ile dict değeri alır."""
    keys = key.split(".")
    value = data
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    return value


def get_exchange_from_config_dict(cfg: Dict[str, Any]) -> BaseExchange:
    """
    Config dict'ine göre exchange döndürür (dosyaya yazmadan test için).
    """
    name = (str(_get("exchange.name", cfg) or "binance")).lower().strip()
    api_key = str(_get("exchange.api_key", cfg) or "")
    api_secret = str(_get("exchange.api_secret", cfg) or "")
    testnet = bool(_get("exchange.testnet", cfg, True))
    paper_trade = bool(_get("exchange.paper_trade", cfg, True))
    fixed_balance = float(_get("account.fixed_balance", cfg) or 1000)

    if name == "binance":
        real_exchange = BinanceFuturesExchange(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet,
        )
    elif name == "mexc":
        real_exchange = MEXCFuturesExchange(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet,
        )
    else:
        real_exchange = BinanceFuturesExchange(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet,
        )

    if paper_trade:
        return PaperTrader(
            initial_balance=fixed_balance,
            data_exchange=real_exchange,
        )
    return real_exchange


def get_exchange(config_path: Optional[str] = None) -> BaseExchange:
    """
    Config dosyasına göre exchange döndürür.

    - exchange.paper_trade true ise: PaperTrader (veri için seçilen borsa kullanılır)
    - exchange.name binance ise: BinanceFuturesExchange
    - exchange.name mexc ise: MEXCFuturesExchange

    Returns:
        BaseExchange instance
    """
    try:
        from ..core.config_manager import ConfigManager
    except ImportError:
        from core.config_manager import ConfigManager

    config = ConfigManager(config_path)
    return get_exchange_from_config_dict(config.get_all())
