"""
Backend API giriş noktası.
Normal çalıştırma: cd backend && set PYTHONPATH=src && python run_api.py
PyInstaller (frozen): exe tek başına çalışır; sys.path otomatik ayarlanır.
"""
import sys
from pathlib import Path

# PyInstaller bundle: _MEIPASS içindeki kodu import edilebilir yap
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    base = Path(getattr(sys, "_MEIPASS", ""))
    if base:
        # datas=('src','') ile bundle'da _MEIPASS/src/ altında api, core, ... var
        src = base / "src"
        if src.exists():
            base = src
        if str(base) not in sys.path:
            sys.path.insert(0, str(base))

import uvicorn

if __name__ == "__main__":
    # Port Electron main.js ile aynı olmalı (8000)
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
