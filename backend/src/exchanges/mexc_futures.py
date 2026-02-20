"""
MEXC Futures Connector - ccxt ile MEXC USDT-M Perpetual (swap) API.

Config: exchange.name, exchange.api_key, exchange.api_secret, exchange.testnet
MEXC'de perpetual için defaultType: 'swap' kullanılır.
"""

from typing import Any, Dict, List, Optional

from .base_exchange import BaseExchange


class MEXCFuturesExchange(BaseExchange):
    """MEXC USDT-M Perpetual Swap."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        testnet: bool = False,
    ):
        self._api_key = api_key
        self._api_secret = api_secret
        self._testnet = testnet
        self._client = None
        self._load_client()

    def _load_client(self) -> None:
        import ccxt

        options = {"defaultType": "swap"}
        self._client = ccxt.mexc({
            "apiKey": self._api_key,
            "secret": self._api_secret,
            "enableRateLimit": True,
            "options": options,
        })
        if self._testnet:
            try:
                self._client.set_sandbox_mode(True)
            except Exception:
                pass  # MEXC sandbox desteklemiyorsa devam et

    def get_balance(self) -> float:
        """USDT cinsinden kullanılabilir bakiye."""
        balance = self._client.fetch_balance()
        if "USDT" in balance.get("total", {}):
            return float(balance["total"].get("USDT") or 0)
        return 0.0

    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Açık pozisyonlar."""
        positions = self._client.fetch_positions()
        out = []
        for p in positions:
            contracts = p.get("contracts")
            if contracts is None:
                continue
            try:
                size = abs(float(contracts))
            except (TypeError, ValueError):
                continue
            if size == 0:
                continue
            sym = p.get("symbol", "")
            if symbol and sym != symbol:
                continue
            side = "long" if float(contracts) > 0 else "short"
            out.append({
                "symbol": sym,
                "side": side,
                "size": size,
                "entry_price": float(p.get("entryPrice") or 0),
                "mark_price": float(p.get("markPrice") or p.get("lastPrice") or 0),
                "unrealized_pnl": float(p.get("unrealizedPnl") or 0),
                "leverage": float(p.get("leverage") or 1),
            })
        return out

    def get_klines(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 500,
    ) -> List[List[Any]]:
        """OHLCV."""
        return self._client.fetch_ohlcv(symbol, timeframe, limit=limit)

    def get_ticker(self, symbol: str) -> Dict[str, float]:
        t = self._client.fetch_ticker(symbol)
        return {
            "last": float(t.get("last") or 0),
            "bid": float(t.get("bid") or 0),
            "ask": float(t.get("ask") or 0),
        }

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "market",
        stop_price: Optional[float] = None,
        reduce_only: bool = False,
    ) -> Dict[str, Any]:
        params = {}
        if reduce_only:
            params["reduceOnly"] = True

        if order_type == "market":
            order = self._client.create_order(
                symbol=symbol,
                type="market",
                side=side,
                amount=quantity,
                params=params,
            )
        else:
            order = self._client.create_order(
                symbol=symbol,
                type="limit",
                side=side,
                amount=quantity,
                price=stop_price or 0,
                params=params,
            )

        return self._normalize_order_response(order, quantity)

    def _normalize_order_response(self, order: Dict, quantity: float) -> Dict[str, Any]:
        filled = float(order.get("filled") or 0)
        avg = order.get("average")
        return {
            "order_id": order.get("id"),
            "symbol": order.get("symbol"),
            "side": order.get("side"),
            "filled": filled,
            "avg_price": float(avg) if avg is not None else None,
            "raw": order,
        }

    def cancel_order(self, order_id: str, symbol: str) -> bool:
        try:
            self._client.cancel_order(order_id, symbol)
            return True
        except Exception:
            return False

    def fetch_order(self, order_id: str, symbol: str) -> Optional[Dict[str, Any]]:
        try:
            return self._client.fetch_order(order_id, symbol)
        except Exception:
            return None
