const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function put<T>(path: string, body: object): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function post<T>(path: string, body?: object): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ---- Config types (backend config_schema ile uyumlu) ----
export interface ExchangeConfig {
  name: string;
  api_key: string;
  api_secret: string;
  testnet: boolean;
  paper_trade: boolean;
}

export interface AccountConfig {
  fixed_balance: number;
  risk_percent: number;
  daily_r_limit: number;
}

export interface TrendFilterConfig {
  timeframe: string;
  ema_period: number;
  macd_fast: number;
  macd_slow: number;
  macd_signal: number;
}

export interface EntryConfig {
  ema_period: number;
  macd_fast: number;
  macd_slow: number;
  macd_signal: number;
  rsi_period: number;
  rsi_threshold: number;
}

export interface StopConfig {
  atr_period: number;
  atr_multiplier: number;
}

export interface TrailingConfig {
  atr_period: number;
  atr_multiplier: number;
  break_even_r: number;
}

export interface StrategyConfig {
  timeframe: string;
  trend_filter: TrendFilterConfig;
  entry: EntryConfig;
  stop: StopConfig;
  trailing: TrailingConfig;
}

export interface SymbolsConfig {
  auto_detect_top_10: boolean;
  manual_list: string[];
}

export interface LoggingConfig {
  level: string;
  log_dir: string | null;
}

export interface TelegramConfig {
  enabled: boolean;
  bot_token: string;
  chat_id: string;
}

export interface AppConfig {
  exchange: ExchangeConfig;
  account: AccountConfig;
  symbols: SymbolsConfig;
  strategy: StrategyConfig;
  logging: LoggingConfig;
  telegram: TelegramConfig;
}

export interface TestConnectionResult {
  ok: boolean;
  message: string;
  balance?: number;
}

export interface ConfigPathResult {
  config_path: string;
}

export interface Stats {
  total_trades: number;
  wins: number;
  losses: number;
  total_pnl: number;
  day_pnl: number;
  win_rate: number;
  avg_pnl: number;
  max_win: number;
  max_loss: number;
  total_r: number;
  day_r: number;
  avg_r: number;
  max_r: number;
  min_r: number;
  total_fees: number;
  day_fees: number;
  trading_disabled_today: boolean;
}

export interface Position {
  symbol: string;
  side: string;
  size: number;
  entry_price: number;
  mark_price: number;
  unrealized_pnl: number;
  leverage: number;
}

export interface Ticker {
  last: number;
  bid: number;
  ask: number;
}

export const api = {
  stats: () => get<Stats>('/api/stats'),
  positions: (symbol?: string) => get<Position[]>(symbol ? `/api/positions?symbol=${encodeURIComponent(symbol)}` : '/api/positions'),
  ticker: (symbol: string = 'BTC/USDT') => get<Ticker>(`/api/ticker?symbol=${encodeURIComponent(symbol)}`),
  balance: () => get<{ balance: number }>('/api/balance'),
  logsTrades: (limit = 100) => get<string[]>(`/api/logs/trades?limit=${limit}`),
  logsSignals: (limit = 100) => get<string[]>(`/api/logs/signals?limit=${limit}`),
  logsTrailing: (limit = 100) => get<string[]>(`/api/logs/trailing?limit=${limit}`),
  lastSignal: () => get<{ raw: string | null; direction: string | null; symbol: string | null }>('/api/last_signal'),
  engineStatus: () => get<{ running: boolean; interval_seconds: number | null }>('/api/engine/status'),
  engineStart: (interval_seconds = 60) => post<{ status: string; interval_seconds: number }>(`/api/engine/start?interval_seconds=${interval_seconds}`),
  engineStop: () => post<{ status: string }>('/api/engine/stop'),

  health: () => get<{ status: string }>('/health'),

  // Config (Settings ekranı için)
  getConfig: () => get<AppConfig>('/api/config'),
  putConfig: (body: AppConfig) => put<AppConfig>('/api/config', body),
  testConnection: (body: AppConfig) => post<TestConnectionResult>('/api/config/test-connection', body),
  getConfigPath: () => get<ConfigPathResult>('/api/config/path'),
};
