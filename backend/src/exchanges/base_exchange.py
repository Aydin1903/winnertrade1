"""
Base Exchange - Tüm exchange connector'lar için abstract interface.

Gerçek borsa (Binance, MEXC) ve paper trader bu interface'i uygular.
Böylece strateji/execution katmanı exchange'e bağımlı olmaz.

Kullanım:
    exchange = get_exchange(config)  # config'ten binance/mexc/paper seçilir
    balance = exchange.get_balance()
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseExchange(ABC):
    """Exchange connector için abstract base class."""

    @abstractmethod
    def get_balance(self) -> float:
        """
        USDT cinsinden kullanılabilir bakiye (margin balance).

        Returns:
            float: Bakiye
        """
        pass

    @abstractmethod
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Açık pozisyonları döndürür.

        Args:
            symbol: None ise tümü, dolu ise sadece o sembol.

        Returns:
            Her pozisyon: {
                'symbol': str,
                'side': 'long' | 'short',
                'size': float,        # kontrat veya base miktar
                'entry_price': float,
                'mark_price': float,
                'unrealized_pnl': float,
                'leverage': int/float
            }
        """
        pass

    @abstractmethod
    def get_klines(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 500,
    ) -> List[List[Any]]:
        """
        Mum (OHLCV) verisi. ccxt format: [timestamp, open, high, low, close, volume].

        Args:
            symbol: Örn. BTCUSDT
            timeframe: 1m, 5m, 15m, 1h, 4h, 1d
            limit: Mum sayısı

        Returns:
            [[ts, o, h, l, c, v], ...]
        """
        pass

    @abstractmethod
    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "market",
        stop_price: Optional[float] = None,
        reduce_only: bool = False,
    ) -> Dict[str, Any]:
        """
        Order gönderir.

        Args:
            symbol: BTCUSDT
            side: 'buy' | 'sell'
            quantity: Miktar (kontrat veya base - exchange'e göre)
            order_type: 'market' | 'limit'
            stop_price: Stop loss/take profit fiyatı (opsiyonel)
            reduce_only: True ise sadece pozisyon kapatır

        Returns:
            { 'order_id': str, 'filled': float, 'avg_price': float, ... }
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Order iptal eder."""
        pass

    def get_ticker(self, symbol: str) -> Dict[str, float]:
        """
        Son fiyat bilgisi. Alt sınıflar override edebilir.

        Returns:
            { 'last': float, 'bid': float, 'ask': float }
        """
        raise NotImplementedError("get_ticker must be implemented")

    def fetch_order(self, order_id: str, symbol: str) -> Optional[Dict[str, Any]]:
        """Order durumunu getirir. İsteğe bağlı."""
        return None
