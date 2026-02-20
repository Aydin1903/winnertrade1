"""
Trailing Stop - Break-even (1R'de zararı sıfırla) + ATR trailing.

Mantık:
  - Fiyat 1R lehimize gidince: stop'u entry'ye çek (break-even).
  - Sonra: stop'u fiyatın arkasından ATR * multiplier ile sürükle (long'da yukarı, short'ta aşağı).
  - Fiyat stop'a gelirse: kapat (should_close=True).
"""

from typing import Literal, Optional, Tuple

try:
    from ..core.config_manager import ConfigManager
except ImportError:
    from core.config_manager import ConfigManager

PositionSide = Literal["long", "short"]


class TrailingStopState:
    """
    Tek bir trade için trailing stop state.
    update(mark_price, atr_value) ile güncellenir; stop'a gelindiğinde should_close True döner.
    """

    def __init__(
        self,
        symbol: str,
        side: PositionSide,
        entry_price: float,
        initial_stop_price: float,
        quantity: float,
        break_even_r: float = 1.0,
        atr_trailing_mult: Optional[float] = None,
    ):
        self.symbol = symbol
        self.side = side
        self.entry_price = entry_price
        self.initial_stop_price = initial_stop_price
        self.quantity = quantity
        self.break_even_r = break_even_r
        if atr_trailing_mult is None:
            config = ConfigManager()
            atr_trailing_mult = float(config.get("strategy.trailing.atr_multiplier") or 1.0)
        self.atr_trailing_mult = atr_trailing_mult

        self.current_stop = initial_stop_price
        self.break_even_done = False
        # 1R fiyat mesafesi (entry'den stop'a uzaklık)
        self._one_r_distance = abs(entry_price - initial_stop_price)

    def update(self, mark_price: float, atr_value: float) -> Tuple[bool, float]:
        """
        Güncel fiyat ve ATR ile stop'u güncelle.

        Returns:
            (should_close, new_stop_price)
            should_close True ise pozisyon kapatılmalı (fiyat stop'a geldi).
        """
        if self.side == "long":
            if mark_price <= self.current_stop:
                return True, self.current_stop
            # Break-even: 1R lehimize gittiyse stop'u entry'ye çek
            if not self.break_even_done and mark_price >= self.entry_price + self._one_r_distance:
                self.break_even_done = True
                self.current_stop = max(self.current_stop, self.entry_price)
            # ATR trailing: stop'u yukarı taşı (fiyat - ATR*mult)
            trail_stop = mark_price - atr_value * self.atr_trailing_mult
            self.current_stop = max(self.current_stop, trail_stop)
            return False, self.current_stop
        else:
            # short
            if mark_price >= self.current_stop:
                return True, self.current_stop
            if not self.break_even_done and mark_price <= self.entry_price - self._one_r_distance:
                self.break_even_done = True
                self.current_stop = min(self.current_stop, self.entry_price)
            trail_stop = mark_price + atr_value * self.atr_trailing_mult
            self.current_stop = min(self.current_stop, trail_stop)
            return False, self.current_stop


def create_trailing_state(
    symbol: str,
    side: PositionSide,
    entry_price: float,
    stop_price: float,
    quantity: float,
    break_even_r: Optional[float] = None,
    atr_trailing_mult: Optional[float] = None,
) -> TrailingStopState:
    """Config'ten break_even_r ve atr_trailing_mult alır; TrailingStopState oluşturur."""
    if break_even_r is None:
        config = ConfigManager()
        break_even_r = float(config.get("strategy.trailing.break_even_r") or 1.0)
    return TrailingStopState(
        symbol=symbol,
        side=side,
        entry_price=entry_price,
        initial_stop_price=stop_price,
        quantity=quantity,
        break_even_r=break_even_r,
        atr_trailing_mult=atr_trailing_mult,
    )
