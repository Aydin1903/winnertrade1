"""
Config Pydantic şeması – doğrulama ve tip güvenliği.
config.example.json yapısı ile uyumlu.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ExchangeConfig(BaseModel):
    name: str = Field(..., description="binance | mexc")
    api_key: str = ""
    api_secret: str = ""
    testnet: bool = True
    paper_trade: bool = True


class AccountConfig(BaseModel):
    fixed_balance: float = Field(1000.0, ge=0, description="Paper trade başlangıç bakiyesi")
    risk_percent: float = Field(1.0, ge=0.01, le=100.0)
    daily_r_limit: float = Field(-3.0, le=0, description="Günlük -3R limiti")


class TrendFilterConfig(BaseModel):
    timeframe: str = "1d"
    ema_period: int = 200
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9


class EntryConfig(BaseModel):
    ema_period: int = 200
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    rsi_period: int = 14
    rsi_threshold: int = 50


class StopConfig(BaseModel):
    atr_period: int = 14
    atr_multiplier: float = 1.5


class TrailingConfig(BaseModel):
    atr_period: int = 14
    atr_multiplier: float = 1.0
    break_even_r: float = 1.0


class StrategyConfig(BaseModel):
    timeframe: str = "15m"
    trend_filter: TrendFilterConfig = Field(default_factory=TrendFilterConfig)
    entry: EntryConfig = Field(default_factory=EntryConfig)
    stop: StopConfig = Field(default_factory=StopConfig)
    trailing: TrailingConfig = Field(default_factory=TrailingConfig)


class SymbolsConfig(BaseModel):
    auto_detect_top_10: bool = True
    manual_list: List[str] = Field(default_factory=lambda: ["BTC/USDT"])


class LoggingConfig(BaseModel):
    level: str = "INFO"
    log_dir: Optional[str] = None  # None = paths.get_log_dir() kullanılır


class TelegramConfig(BaseModel):
    enabled: bool = False
    bot_token: str = ""
    chat_id: str = ""


class AppConfig(BaseModel):
    """Tüm uygulama config'i."""

    exchange: ExchangeConfig = Field(default_factory=ExchangeConfig)
    account: AccountConfig = Field(default_factory=AccountConfig)
    symbols: SymbolsConfig = Field(default_factory=SymbolsConfig)
    strategy: StrategyConfig = Field(default_factory=StrategyConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)

    class Config:
        extra = "ignore"
