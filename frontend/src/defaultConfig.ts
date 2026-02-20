import type { AppConfig } from './services/api';

/** Config yokken (ilk kurulum veya 404) kullanılacak varsayılan config. */
export function defaultAppConfig(): AppConfig {
  return {
    exchange: {
      name: 'binance',
      api_key: '',
      api_secret: '',
      testnet: true,
      paper_trade: true,
    },
    account: {
      fixed_balance: 1000,
      risk_percent: 1,
      daily_r_limit: -3,
    },
    symbols: {
      auto_detect_top_10: true,
      manual_list: ['BTC/USDT'],
    },
    strategy: {
      timeframe: '15m',
      trend_filter: {
        timeframe: '1d',
        ema_period: 200,
        macd_fast: 12,
        macd_slow: 26,
        macd_signal: 9,
      },
      entry: {
        ema_period: 200,
        macd_fast: 12,
        macd_slow: 26,
        macd_signal: 9,
        rsi_period: 14,
        rsi_threshold: 50,
      },
      stop: { atr_period: 14, atr_multiplier: 1.5 },
      trailing: { atr_period: 14, atr_multiplier: 1, break_even_r: 1 },
    },
    logging: { level: 'INFO', log_dir: null },
    telegram: { enabled: false, bot_token: '', chat_id: '' },
  };
}
