"""
Global State - Uygulama genelinde paylaşılan state

Kullanım:
    from core.state import AppState
    
    state = AppState()
    state.trading_disabled_today = True
    if state.can_trade():
        # Trade yap
"""

from datetime import datetime, date
from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class AppState:
    """Uygulama global state"""
    
    # Trading durumu
    trading_disabled_today: bool = False
    last_reset_date: Optional[date] = None
    
    # Bakiyeler
    fixed_balance: float = 0.0
    current_balance: float = 0.0
    
    # Günlük R değerleri
    day_r: float = 0.0
    
    # Aktif pozisyonlar
    positions: Dict[str, dict] = field(default_factory=dict)
    
    def reset_daily(self) -> None:
        """Günlük değerleri sıfırla (yeni gün başlangıcında)"""
        today = date.today()
        
        if self.last_reset_date != today:
            self.trading_disabled_today = False
            self.day_r = 0.0
            self.last_reset_date = today
    
    def can_trade(self) -> bool:
        """Trade yapılabilir mi?"""
        self.reset_daily()
        return not self.trading_disabled_today
    
    def add_day_r(self, r_value: float) -> None:
        """Günlük R değerine ekle"""
        self.reset_daily()
        self.day_r += r_value
        
        # Günlük limit kontrolü
        from core.config_manager import ConfigManager
        config = ConfigManager()
        daily_limit = config.get('account.daily_r_limit', -3.0)
        
        if self.day_r <= daily_limit:
            self.trading_disabled_today = True
    
    def get_day_r(self) -> float:
        """Günlük R değerini al"""
        self.reset_daily()
        return self.day_r
