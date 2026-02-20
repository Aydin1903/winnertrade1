"""
Config Manager - Config dosyasını yönetir ve yükler.
Storage + Pydantic şema kullanır; yol paths modülünden gelir (AppData / proje config).
Mevcut get/set/save/get_all API'si korunur.

Kullanım:
    from core.config_manager import ConfigManager

    config = ConfigManager()
    exchange_name = config.get('exchange.name')
"""

from pathlib import Path
from typing import Any, Dict, Optional

from core.paths import get_config_path
from core.config_schema import AppConfig
from storage.config_storage import ConfigStorage


class ConfigManager:
    """Config dosyasını yönetir (storage + şema doğrulama)."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Args:
            config_path: Config dosyası yolu. None ise paths.get_config_path() kullanılır
                         (AppData veya proje config/config.json).
        """
        path = Path(config_path) if config_path else get_config_path()
        self._storage = ConfigStorage(path)
        self.config_path = self._storage.path
        self._config: Dict[str, Any] = {}
        if self._storage.exists():
            self.load()

    def load(self) -> None:
        """Config dosyasını yükler ve şema ile doğrular."""
        if not self._storage.exists():
            raise FileNotFoundError(
                f"Config dosyası bulunamadı: {self.config_path}\n"
                "İlk çalıştırmada Setup ekranından ayarları yapın veya config örneğini kopyalayın."
            )
        config = self._storage.load()
        self._config = config.model_dump()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Config değerini alır (nokta notasyonu ile).

        Örnek:
            config.get('exchange.name')
            config.get('strategy.timeframe')
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Config değerini ayarlar (nokta notasyonu ile).

        Örnek:
            config.set('exchange.testnet', False)
        """
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def save(self) -> None:
        """Config'i şema ile doğrulayıp dosyaya yazar."""
        config = AppConfig.model_validate(self._config)
        self._storage.save(config)

    def get_all(self) -> Dict[str, Any]:
        """Tüm config'i döndür (kopya)."""
        return self._config.copy()
