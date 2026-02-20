"""
Trading engine'i başlatır.

Çalıştırma (proje kökünden veya backend'den):
  cd backend
  set PYTHONPATH=src
  python scripts/run_engine.py

Veya:
  python -m engine
"""
import sys
from pathlib import Path

backend = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend / "src"))

from engine.loop import run_engine

if __name__ == "__main__":
    # 60 saniyede bir sinyal + trailing kontrolü
    run_engine(interval_seconds=60)
