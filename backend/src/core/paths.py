"""
Uygulama yolları – Windows AppData, config ve log dizinleri.

Production (PyInstaller / tek exe): AppData/Local/winnertrade
Geliştirme: Proje root'una göre config/ ve backend/logs/ kullanılabilir.
"""

import os
import sys
from pathlib import Path

# PyInstaller bundle içinde mi çalışıyoruz?
def _is_frozen() -> bool:
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def get_app_data_root() -> Path:
    """
    Uygulama veri kökü.
    Windows: %LOCALAPPDATA%\\winnertrade
    Diğer: ~/.local/share/winnertrade (Linux/macOS)
    """
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        return Path(base) / "winnertrade"
    return Path.home() / ".local" / "share" / "winnertrade"


def get_config_path() -> Path:
    """
    Config dosyası yolu.
    Production: AppData/Local/winnertrade/config.json
    Geliştirme (config yoksa): proje root/config/config.json
    """
    if _is_frozen():
        return get_app_data_root() / "config.json"
    # Geliştirme: önce AppData'a bak, yoksa proje config'ine
    app_data_config = get_app_data_root() / "config.json"
    if app_data_config.exists():
        return app_data_config
    # Proje root = backend'in 2 üstü
    try:
        project_root = Path(__file__).resolve().parent.parent.parent
        return project_root / "config" / "config.json"
    except Exception:
        return app_data_config


def get_log_dir() -> Path:
    """
    Log dizini.
    Production: AppData/Local/winnertrade/logs
    Geliştirme: backend/logs (proje içi)
    """
    if _is_frozen():
        log_dir = get_app_data_root() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    try:
        project_root = Path(__file__).resolve().parent.parent.parent
        log_dir = project_root / "backend" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    except Exception:
        log_dir = get_app_data_root() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir


def ensure_app_data_dir() -> Path:
    """AppData winnertrade dizinini oluşturur; config yoksa first-run için hazırlar."""
    root = get_app_data_root()
    root.mkdir(parents=True, exist_ok=True)
    return root
