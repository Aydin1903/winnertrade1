"""
Config dosyası okuma/yazma – AppData veya proje config path kullanır.
Pydantic şema ile doğrulama.
"""

import json
from pathlib import Path
from typing import Any, Dict

from core.paths import ensure_app_data_dir, get_config_path
from core.config_schema import AppConfig


class ConfigStorage:
    """Config dosyasını okur, yazar ve doğrular."""

    def __init__(self, config_path: Path | None = None):
        self._path = config_path or get_config_path()
        self._raw: Dict[str, Any] = {}

    @property
    def path(self) -> Path:
        return self._path

    def exists(self) -> bool:
        return self._path.exists()

    def load_raw(self) -> Dict[str, Any]:
        """Dosyadan ham JSON yükler; doğrulama yapmaz."""
        if not self._path.exists():
            raise FileNotFoundError(
                f"Config dosyası bulunamadı: {self._path}\n"
                "İlk çalıştırmada Setup ekranından ayarları yapın veya config örneğini kopyalayın."
            )
        with open(self._path, "r", encoding="utf-8") as f:
            self._raw = json.load(f)
        return self._raw.copy()

    def load(self) -> AppConfig:
        """Config dosyasını yükler ve Pydantic ile doğrular."""
        raw = self.load_raw()
        return AppConfig.model_validate(raw)

    def save(self, config: AppConfig) -> None:
        """Config'i dosyaya yazar. Dizin yoksa oluşturur."""
        if self._path == get_config_path():
            ensure_app_data_dir()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)
        self._raw = config.model_dump()

    def save_raw(self, data: Dict[str, Any]) -> None:
        """Ham dict'i doğrulayıp kaydeder. Geçersiz veri hata fırlatır."""
        config = AppConfig.model_validate(data)
        self.save(config)

    @staticmethod
    def default_config_path() -> Path:
        return get_config_path()
