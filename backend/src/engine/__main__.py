"""
Çalıştırma: cd backend && set PYTHONPATH=src && python -m engine
"""
from .loop import run_engine

if __name__ == "__main__":
    run_engine(interval_seconds=60)
