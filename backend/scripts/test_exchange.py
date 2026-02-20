"""
Exchange bağlantı testi.

Çalıştırma (proje kökünden, config/config.json dolu olmalı):
  cd backend
  set PYTHONPATH=src
  python scripts/test_exchange.py

Veya:
  cd backend
  python -c "import sys; sys.path.insert(0,'src'); from exchanges.factory import get_exchange; e=get_exchange(); print('Balance', e.get_balance()); print('BTCUSDT ticker', e.get_ticker('BTC/USDT'))"
"""

import sys
from pathlib import Path

# backend/scripts -> backend/src path
backend = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend / "src"))

def main():
    from exchanges.factory import get_exchange

    exchange = get_exchange()
    print("Exchange tipi:", type(exchange).__name__)
    balance = exchange.get_balance()
    print("Bakiye (USDT):", balance)
    try:
        ticker = exchange.get_ticker("BTC/USDT")
        print("BTC/USDT son fiyat:", ticker.get("last"))
    except Exception as err:
        print("Ticker hatası (API key veya network):", err)
    print("Tamamlandı.")

if __name__ == "__main__":
    main()
