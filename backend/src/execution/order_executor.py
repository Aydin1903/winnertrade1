"""
Order Executor - Pozisyon açma ve kapatma (market order).

Exchange interface: place_order(symbol, side, quantity, order_type, reduce_only).
side: 'buy' | 'sell'  (long = buy, short = sell; kapatma = tersi + reduce_only)
"""

from typing import Any, Dict, Literal, Optional

OrderSide = Literal["buy", "sell"]
PositionSide = Literal["long", "short"]


def _to_order_side(position_side: PositionSide) -> OrderSide:
    return "buy" if position_side == "long" else "sell"


def open_position(
    exchange,
    symbol: str,
    side: PositionSide,
    quantity: float,
    order_type: str = "market",
) -> Dict[str, Any]:
    """
    Yeni pozisyon açar (market).

    Args:
        exchange: BaseExchange
        symbol: BTC/USDT veya BTCUSDT (exchange formatında)
        side: 'long' | 'short'
        quantity: Base cinsinden miktar (örn. BTC)
        order_type: 'market' (varsayılan)

    Returns:
        place_order cevabı: order_id, filled, avg_price, ...
    """
    order_side = _to_order_side(side)
    return exchange.place_order(
        symbol=symbol,
        side=order_side,
        quantity=quantity,
        order_type=order_type,
        reduce_only=False,
    )


def close_position(
    exchange,
    symbol: str,
    side: PositionSide,
    quantity: float,
    order_type: str = "market",
) -> Dict[str, Any]:
    """
    Pozisyon kapatır (reduce_only market).

    Args:
        exchange: BaseExchange
        symbol: Aynı sembol
        side: Mevcut pozisyon yönü ('long' ise kapatmak için sell gönderilir)
        quantity: Kapatılacak miktar

    Returns:
        place_order cevabı
    """
    close_side = "sell" if side == "long" else "buy"
    return exchange.place_order(
        symbol=symbol,
        side=close_side,
        quantity=quantity,
        order_type=order_type,
        reduce_only=True,
    )
