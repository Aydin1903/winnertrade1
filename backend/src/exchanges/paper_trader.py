"""
Paper Trader - Gerçek para kullanmadan trade simülasyonu.

Piyasa verisi (klines, ticker) bir BaseExchange'den alınır.
Bakiye ve pozisyonlar bellekte tutulur; order'lar anlık fiyattan doldurulmuş kabul edilir.
"""

from typing import Any, Dict, List, Optional

from .base_exchange import BaseExchange


class PaperTrader(BaseExchange):
    """
    Paper trade: Order'lar gerçek gönderilmez, anlık fiyattan doldurulmuş kabul edilir.
    data_exchange: Sadece get_klines ve get_ticker için kullanılır (piyasa verisi).
    """

    def __init__(
        self,
        initial_balance: float,
        data_exchange: BaseExchange,
    ):
        self._balance = float(initial_balance)
        self._data = data_exchange
        # symbol -> { side, size, entry_price }
        self._positions: Dict[str, Dict[str, Any]] = {}

    def get_balance(self) -> float:
        return self._balance

    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        ticker = self._data.get_ticker if hasattr(self._data, "get_ticker") else None
        out = []
        for sym, pos in list(self._positions.items()):
            if symbol and sym != symbol:
                continue
            mark = pos.get("entry_price")
            if ticker and sym:
                try:
                    t = ticker(sym)
                    mark = t.get("last") or mark
                except Exception:
                    pass
            size = pos["size"]
            entry = pos["entry_price"]
            side = pos["side"]
            if side == "long":
                unrealized = (mark - entry) * size
            else:
                unrealized = (entry - mark) * size
            out.append({
                "symbol": sym,
                "side": side,
                "size": size,
                "entry_price": entry,
                "mark_price": mark,
                "unrealized_pnl": unrealized,
                "leverage": 1,
            })
        return out

    def get_klines(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 500,
    ) -> List[List[Any]]:
        return self._data.get_klines(symbol, timeframe, limit)

    def get_ticker(self, symbol: str) -> Dict[str, float]:
        return self._data.get_ticker(symbol)

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "market",
        stop_price: Optional[float] = None,
        reduce_only: bool = False,
    ) -> Dict[str, Any]:
        """Simüle: Anlık fiyattan doldurulmuş kabul edilir."""
        ticker = self._data.get_ticker(symbol)
        price = float(ticker.get("last") or ticker.get("bid") or ticker.get("ask") or 0)
        if price <= 0:
            return {"order_id": None, "filled": 0, "avg_price": None, "error": "no price"}

        filled = quantity
        cost = quantity * price

        if reduce_only:
            # Pozisyon kapatma
            pos = self._positions.get(symbol)
            if not pos:
                return {"order_id": "paper-close", "filled": 0, "avg_price": price, "raw": {}}
            close_side = "sell" if pos["side"] == "long" else "buy"
            if close_side != side:
                return {"order_id": "paper-close", "filled": 0, "avg_price": price, "raw": {}}
            close_size = min(quantity, pos["size"])
            if pos["side"] == "long":
                pnl = (price - pos["entry_price"]) * close_size
            else:
                pnl = (pos["entry_price"] - price) * close_size
            self._balance += pnl
            pos["size"] -= close_size
            if pos["size"] <= 0:
                del self._positions[symbol]
            return {
                "order_id": "paper-reduce",
                "symbol": symbol,
                "side": side,
                "filled": close_size,
                "avg_price": price,
                "raw": {},
            }

        # Yeni pozisyon veya ekleme
        if symbol in self._positions:
            pos = self._positions[symbol]
            if pos["side"] == ("long" if side == "buy" else "short"):
                # Aynı yönde ekleme: ortalama fiyat
                old_size = pos["size"]
                old_entry = pos["entry_price"]
                new_size = old_size + quantity
                pos["entry_price"] = (old_entry * old_size + price * quantity) / new_size
                pos["size"] = new_size
            else:
                # Ters yön: kapatma
                close_size = min(quantity, pos["size"])
                if pos["side"] == "long":
                    pnl = (price - pos["entry_price"]) * close_size
                else:
                    pnl = (pos["entry_price"] - price) * close_size
                self._balance += pnl
                pos["size"] -= close_size
                if pos["size"] <= 0:
                    del self._positions[symbol]
                filled = close_size
        else:
            self._positions[symbol] = {
                "side": "long" if side == "buy" else "short",
                "size": quantity,
                "entry_price": price,
            }
        return {
            "order_id": "paper-" + symbol,
            "symbol": symbol,
            "side": side,
            "filled": filled,
            "avg_price": price,
            "raw": {},
        }

    def cancel_order(self, order_id: str, symbol: str) -> bool:
        return True  # Paper'da bekleyen order yok

    def fetch_order(self, order_id: str, symbol: str) -> Optional[Dict[str, Any]]:
        return None
