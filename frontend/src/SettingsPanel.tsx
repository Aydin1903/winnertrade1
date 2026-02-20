import { useEffect, useState } from 'react';
import { api, type AppConfig } from './services/api';
import { defaultAppConfig } from './defaultConfig';
import { toFriendlyApiError, toFriendlyConnectionError } from './utils/apiErrors';

const API_SECRET_MASK = '********';

type SaveStatus = 'idle' | 'saving' | 'ok' | 'error';
type TestStatus = 'idle' | 'testing' | 'ok' | 'error';

interface SettingsPanelProps {
  /** İlk kurulumda config kaydedildikten sonra ana ekrana geçmek için çağrılır. */
  onConfigSaved?: () => void;
}

export default function SettingsPanel({ onConfigSaved }: SettingsPanelProps) {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [saveErrorMessage, setSaveErrorMessage] = useState<string>('');
  const [testStatus, setTestStatus] = useState<TestStatus>('idle');
  const [testMessage, setTestMessage] = useState<string>('');
  const [configPath, setConfigPath] = useState<string | null>(null);

  const loadConfig = async () => {
    setLoading(true);
    try {
      const cfg = await api.getConfig();
      setConfig(cfg);
    } catch {
      setConfig(defaultAppConfig());
    } finally {
      setLoading(false);
    }
  };

  const loadConfigPath = async () => {
    try {
      const { config_path } = await api.getConfigPath();
      setConfigPath(config_path);
    } catch {
      setConfigPath(null);
    }
  };

  useEffect(() => {
    loadConfig();
    loadConfigPath();
  }, []);

  const updateExchange = <K extends keyof AppConfig['exchange']>(key: K, value: AppConfig['exchange'][K]) => {
    setConfig((c) => (c ? { ...c, exchange: { ...c.exchange, [key]: value } } : null));
  };
  const updateAccount = <K extends keyof AppConfig['account']>(key: K, value: AppConfig['account'][K]) => {
    setConfig((c) => (c ? { ...c, account: { ...c.account, [key]: value } } : null));
  };
  const updateSymbols = (patch: Partial<AppConfig['symbols']>) => {
    setConfig((c) => (c ? { ...c, symbols: { ...c.symbols, ...patch } } : null));
  };

  const handleSave = async () => {
    if (!config) return;
    setSaveStatus('saving');
    try {
      await api.putConfig(config);
      setSaveStatus('ok');
      onConfigSaved?.();
      setTimeout(() => setSaveStatus('idle'), 2500);
    } catch (e) {
      setSaveStatus('error');
      setSaveErrorMessage(toFriendlyApiError(e));
      setTimeout(() => { setSaveStatus('idle'); setSaveErrorMessage(''); }, 4000);
    }
  };

  const handleTestConnection = async () => {
    if (!config) return;
    setTestStatus('testing');
    setTestMessage('');
    try {
      const result = await api.testConnection(config);
      setTestStatus('ok');
      setTestMessage(result.ok ? `Bağlantı başarılı.${result.balance != null ? ` Bakiye: ${result.balance}` : ''}` : result.message || '');
    } catch (e) {
      setTestStatus('error');
      setTestMessage(toFriendlyConnectionError(e));
    }
  };

  if (loading || !config) {
    return (
      <div className="panel-section">
        <p className="muted">Ayarlar yükleniyor…</p>
      </div>
    );
  }

  const manualListStr = config.symbols.manual_list.join(', ');
  const setManualListStr = (s: string) =>
    updateSymbols({ manual_list: s.split(/[\s,]+/).filter(Boolean).map((x) => x.trim()) });

  return (
    <div className="panel-section settings-panel">
      <h3>Borsa (Exchange)</h3>
      <div className="settings-grid">
        <label className="settings-field">
          <span className="settings-label">Borsa</span>
          <select
            value={config.exchange.name}
            onChange={(e) => updateExchange('name', e.target.value as 'binance' | 'mexc')}
          >
            <option value="binance">Binance Futures</option>
            <option value="mexc">MEXC Futures</option>
          </select>
        </label>
        <label className="settings-field">
          <span className="settings-label">API Key</span>
          <input
            type="text"
            value={config.exchange.api_key}
            onChange={(e) => updateExchange('api_key', e.target.value)}
            placeholder="API anahtarınız"
            autoComplete="off"
          />
        </label>
        <label className="settings-field">
          <span className="settings-label">API Secret</span>
          <input
            type="password"
            value={config.exchange.api_secret}
            onChange={(e) => updateExchange('api_secret', e.target.value)}
            placeholder={config.exchange.api_secret === API_SECRET_MASK ? '••••••••' : ''}
            autoComplete="off"
          />
          {config.exchange.api_secret === API_SECRET_MASK && (
            <span className="settings-hint">Mevcut değer korunuyor; değiştirmek için yeni girin.</span>
          )}
        </label>
        <label className="settings-field settings-check">
          <input
            type="checkbox"
            checked={config.exchange.testnet}
            onChange={(e) => updateExchange('testnet', e.target.checked)}
          />
          <span className="settings-label">Testnet kullan</span>
        </label>
        <label className="settings-field settings-check">
          <input
            type="checkbox"
            checked={config.exchange.paper_trade}
            onChange={(e) => updateExchange('paper_trade', e.target.checked)}
          />
          <span className="settings-label">Paper trade (simülasyon)</span>
        </label>
      </div>

      <h3>Hesap & Risk</h3>
      <div className="settings-grid">
        <label className="settings-field">
          <span className="settings-label">Sabit bakiye (USDT)</span>
          <input
            type="number"
            min={0}
            step={100}
            value={config.account.fixed_balance}
            onChange={(e) => updateAccount('fixed_balance', Number(e.target.value) || 0)}
          />
        </label>
        <label className="settings-field">
          <span className="settings-label">Risk % (işlem başına)</span>
          <input
            type="number"
            min={0.01}
            max={100}
            step={0.1}
            value={config.account.risk_percent}
            onChange={(e) => updateAccount('risk_percent', Number(e.target.value) || 1)}
          />
        </label>
        <label className="settings-field">
          <span className="settings-label">Günlük R limiti</span>
          <input
            type="number"
            max={0}
            step={0.5}
            value={config.account.daily_r_limit}
            onChange={(e) => updateAccount('daily_r_limit', Number(e.target.value) || -3)}
          />
        </label>
      </div>

      <h3>Semboller</h3>
      <div className="settings-grid">
        <label className="settings-field settings-check">
          <input
            type="checkbox"
            checked={config.symbols.auto_detect_top_10}
            onChange={(e) => updateSymbols({ auto_detect_top_10: e.target.checked })}
          />
          <span className="settings-label">Hacme göre ilk 10 sembolü otomatik seç</span>
        </label>
        <label className="settings-field settings-full">
          <span className="settings-label">Manuel sembol listesi (virgül veya boşlukla ayırın)</span>
          <input
            type="text"
            value={manualListStr}
            onChange={(e) => setManualListStr(e.target.value)}
            placeholder="BTC/USDT, ETH/USDT"
          />
        </label>
      </div>

      <div className="settings-actions">
        <button type="button" className="btn-settings primary" onClick={handleSave} disabled={saveStatus === 'saving'}>
          {saveStatus === 'saving' ? 'Kaydediliyor…' : 'Kaydet'}
        </button>
        <button
          type="button"
          className="btn-settings secondary"
          onClick={handleTestConnection}
          disabled={testStatus === 'testing'}
        >
          {testStatus === 'testing' ? 'Test ediliyor…' : 'Bağlantıyı test et'}
        </button>
      </div>
      {saveStatus === 'ok' && <p className="settings-feedback positive">Ayarlar kaydedildi.</p>}
      {saveStatus === 'error' && saveErrorMessage && <p className="settings-feedback negative">{saveErrorMessage}</p>}
      {testStatus === 'ok' && testMessage && <p className="settings-feedback positive">{testMessage}</p>}
      {testStatus === 'error' && testMessage && <p className="settings-feedback negative">{testMessage}</p>}
      {configPath && (
        <p className="settings-path muted">
          Config dosyası: <code>{configPath}</code>
        </p>
      )}
    </div>
  );
}
