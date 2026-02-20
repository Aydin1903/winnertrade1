"""
Risk Manager - R hesabı, position size, günlük limit kontrolü.

Formüller:
  risk_amount = fixed_balance * (risk_percent / 100)
  position_size = risk_amount / stop_distance   (stop_distance = fiyat cinsinden stop mesafesi)
  1 R = risk_amount (USDT cinsinden riske edilen miktar)
  trade R = pnl_usdt / risk_amount

Kullanım (execution katmanında):
  - Yeni trade öncesi: can_open_trade(state) ve risk_manager.get_position_size(stop_distance)
  - Trade kapandığında: r = RiskManager.pnl_to_r(pnl_usdt, risk_amount); state.add_day_r(r)
"""

from typing import Optional

try:
    from ..core.config_manager import ConfigManager
except ImportError:
    from core.config_manager import ConfigManager


class RiskManager:
    """Risk hesaplamaları ve günlük limit."""

    def __init__(
        self,
        fixed_balance: Optional[float] = None,
        risk_percent: Optional[float] = None,
        daily_r_limit: Optional[float] = None,
    ):
        """
        None verilen değerler config'ten okunur.
        """
        config = ConfigManager()
        self._fixed_balance = fixed_balance if fixed_balance is not None else float(config.get("account.fixed_balance") or 1000)
        self._risk_percent = risk_percent if risk_percent is not None else float(config.get("account.risk_percent") or 1.0)
        self._daily_r_limit = daily_r_limit if daily_r_limit is not None else float(config.get("account.daily_r_limit") or -3.0)

    def get_risk_amount(self) -> float:
        """1 R = riske edilen USDT miktarı."""
        return self._fixed_balance * (self._risk_percent / 100.0)

    def get_position_size(
        self,
        stop_distance: float,
        risk_amount: Optional[float] = None,
    ) -> float:
        """
        Pozisyon büyüklüğü (base cinsinden miktar).

        Args:
            stop_distance: Stop ile entry arasındaki fiyat farkı (tek birim için, örn. 1 BTC başına USDT).
            risk_amount: None ise config'ten hesaplanır.

        Returns:
            Miktar (örn. BTC için kaç BTC).
        """
        if stop_distance <= 0:
            return 0.0
        ra = risk_amount if risk_amount is not None else self.get_risk_amount()
        return ra / stop_distance

    @staticmethod
    def pnl_to_r(pnl_usdt: float, risk_amount: float) -> float:
        """
        Trade PnL (USDT) -> R değeri.
        1 R = risk_amount olduğu için: R = pnl_usdt / risk_amount.
        """
        if risk_amount <= 0:
            return 0.0
        return pnl_usdt / risk_amount

    @staticmethod
    def r_to_pnl(r: float, risk_amount: float) -> float:
        """R -> USDT PnL (teorik)."""
        return r * risk_amount

    def get_daily_r_limit(self) -> float:
        """Günlük R limiti (örn. -3)."""
        return self._daily_r_limit

    def get_fixed_balance(self) -> float:
        return self._fixed_balance

    def get_risk_percent(self) -> float:
        return self._risk_percent


def can_open_trade(state) -> bool:
    """
    Bugün yeni trade açılabilir mi?
    State'in can_trade() ve günlük limit kontrolü kullanılır.
    """
    return state.can_trade()


def stop_distance_price(entry_price: float, stop_price: float, side: str = "") -> float:
    """
    Entry ile stop arasındaki fiyat farkı (tek birim için, USDT).
    Long: stop aşağıda -> entry - stop_price
    Short: stop yukarıda -> stop_price - entry
    """
    return abs(entry_price - stop_price)
