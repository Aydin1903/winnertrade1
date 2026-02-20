import { useEffect, useState } from 'react';
import type { Stats, Position, Ticker } from './services/api';
import { api } from './services/api';
import { isNetworkError, toFriendlyApiError } from './utils/apiErrors';
import SettingsPanel from './SettingsPanel';

/** Veri yenileme aralığı (ms). Daha hızlı için 500–800 kullanılabilir; backend yükü artar. */
const REFRESH_MS = 1000;
const DEFAULT_SYMBOL = 'BTC/USDT';

export default function App() {
  /** null = henüz bilinmiyor, true = config yok (kurulum gerekli), false = config var (ana ekran). */
  const [needsSetup, setNeedsSetup] = useState<boolean | null>(null);
  /** Backend'e ulaşılamıyor (ağ/bağlantı hatası). */
  const [backendUnreachable, setBackendUnreachable] = useState(false);

  const [stats, setStats] = useState<Stats | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [ticker, setTicker] = useState<Ticker | null>(null);
  const [lastSignal, setLastSignal] = useState<string | null>(null);
  const [tradesLog, setTradesLog] = useState<string[]>([]);
  const [signalsLog, setSignalsLog] = useState<string[]>([]);
  const [trailingLog, setTrailingLog] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<'position' | 'stats' | 'trades' | 'trailing' | 'signals' | 'settings'>('position');
  const [error, setError] = useState<string | null>(null);
  const [engineRunning, setEngineRunning] = useState(false);
  const [engineLoading, setEngineLoading] = useState(false);

  const fetchAll = async () => {
    try {
      setError(null);
      const [s, p, t, ls, tl, sl, tr, eng] = await Promise.all([
        api.stats(),
        api.positions(),
        api.ticker(DEFAULT_SYMBOL),
        api.lastSignal().then((r) => r.raw),
        api.logsTrades(),
        api.logsSignals(),
        api.logsTrailing(),
        api.engineStatus().catch(() => ({ running: false, interval_seconds: null })),
      ]);
      setStats(s);
      setPositions(p);
      setTicker(t);
      setLastSignal(ls);
      setTradesLog(tl);
      setSignalsLog(sl);
      setTrailingLog(tr);
      setEngineRunning(eng.running);
    } catch (e) {
      setError(toFriendlyApiError(e));
    }
  };

  const handleEngineStart = async () => {
    setEngineLoading(true);
    try {
      await api.engineStart(60);
      setEngineRunning(true);
    } catch (e) {
      setError(toFriendlyApiError(e));
    } finally {
      setEngineLoading(false);
    }
  };

  const handleEngineStop = async () => {
    setEngineLoading(true);
    try {
      await api.engineStop();
      setEngineRunning(false);
    } catch (e) {
      setError(toFriendlyApiError(e));
    } finally {
      setEngineLoading(false);
    }
  };

  const checkConfigAndBackend = () => {
    setBackendUnreachable(false);
    api.getConfig()
      .then(() => {
        setNeedsSetup(false);
        setBackendUnreachable(false);
      })
      .catch((e) => {
        if (isNetworkError(e)) {
          setBackendUnreachable(true);
        } else {
          setNeedsSetup(true);
        }
      });
  };

  // Config var mı / backend erişilebilir mi (ilk açılış)
  useEffect(() => {
    checkConfigAndBackend();
  }, []);

  // Ana ekran verisi yalnızca config varsa yenilenir
  useEffect(() => {
    if (needsSetup !== false) return;
    fetchAll();
    const id = setInterval(fetchAll, REFRESH_MS);
    return () => clearInterval(id);
  }, [needsSetup]);

  const livePnl = positions.reduce((acc, p) => acc + (p.unrealized_pnl || 0), 0);

  // Henüz config kontrolü yapılmadı
  if (needsSetup === null && !backendUnreachable) {
    return (
      <div className="app app-loading">
        <div className="setup-loading">
          <p>Kontrol ediliyor…</p>
        </div>
      </div>
    );
  }

  // Backend'e ulaşılamıyor
  if (backendUnreachable) {
    return (
      <div className="app app-loading">
        <div className="setup-loading error-box">
          <p className="error-title">Backend'e bağlanılamıyor</p>
          <p className="error-desc">Lütfen backend'in çalıştığından emin olun (örn. <code>uvicorn api.main:app --port 8000</code>).</p>
          <button type="button" className="btn-settings primary" onClick={checkConfigAndBackend}>Yeniden dene</button>
        </div>
      </div>
    );
  }

  // Config yok: sadece kurulum ekranı
  if (needsSetup) {
    return (
      <div className="app">
        <header className="top-bar setup-header" style={{ position: 'relative' }}>
          <span className="item"><span className="label">WinnerTrade</span><span className="value">İlk kurulum</span></span>
        </header>
        <div className="panels">
          <div className="panel-content setup-content">
            <p className="setup-intro">Config dosyası bulunamadı. Aşağıdaki ayarları yapıp <strong>Kaydet</strong> ile devam edin.</p>
            <SettingsPanel onConfigSaved={() => setNeedsSetup(false)} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="top-bar" style={{ position: 'relative' }}>
        <span className="item"><span className="label">Last Signal</span><span className="value muted">{lastSignal ?? '—'}</span></span>
        <span className="item"><span className="label">Last Price</span><span className="value">{typeof ticker?.last === 'number' ? ticker.last.toLocaleString(undefined, { minimumFractionDigits: 2 }) : '—'}</span></span>
        <span className="item"><span className="label">Live PnL</span><span className={`value ${livePnl >= 0 ? 'positive' : 'negative'}`}>{livePnl.toFixed(2)}</span></span>
        <span className="item"><span className="label">Total PnL</span><span className={`value ${(stats?.total_pnl ?? 0) >= 0 ? 'positive' : 'negative'}`}>{stats?.total_pnl?.toFixed(2) ?? '—'}</span></span>
        <span className="item"><span className="label">Day PnL</span><span className={`value ${(stats?.day_pnl ?? 0) >= 0 ? 'positive' : 'negative'}`}>{stats?.day_pnl?.toFixed(2) ?? '—'}</span></span>
        <span className="item"><span className="label">Win Rate</span><span className="value">{stats?.win_rate ?? '—'}%</span></span>
        <span className="item"><span className="label">Total R</span><span className="value">{stats?.total_r ?? '—'}</span></span>
        <span className="item"><span className="label">Day R</span><span className="value">{stats?.day_r ?? '—'}</span></span>
        <span className="item"><span className="label">Total Fees</span><span className="value muted">{stats?.total_fees ?? '—'}</span></span>
        <span className="item"><span className="label">Day Fees</span><span className="value muted">{stats?.day_fees ?? '—'}</span></span>
        {stats?.trading_disabled_today && <span className="badge negative">Trading disabled today</span>}
        <span className="item engine-control">
          {engineRunning ? (
            <>
              <span className="value positive">Engine ON</span>
              <button type="button" className="btn-engine stop" onClick={handleEngineStop} disabled={engineLoading}>Stop</button>
            </>
          ) : (
            <button type="button" className="btn-engine start" onClick={handleEngineStart} disabled={engineLoading}>Start Engine</button>
          )}
        </span>
      </header>

      {error && <div className="error">{error}</div>}

      <div className="panels">
        <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
          <div className="panel-tabs">
            {(['position', 'stats', 'trades', 'trailing', 'signals', 'settings'] as const).map((tab) => (
              <button key={tab} className={activeTab === tab ? 'active' : ''} onClick={() => setActiveTab(tab)}>
                {tab === 'settings' ? 'Ayarlar' : tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
          <div className="panel-content">
            {activeTab === 'position' && (
              <div className="panel-section">
                <h3>Position</h3>
                {positions.length === 0 ? <div className="muted">No open positions</div> : positions.map((p, i) => (
                  <div key={i} className="position-row">
                    <span className="symbol">{p.symbol}</span>
                    <span className={`side ${p.side}`}>{p.side}</span>
                    <span>Size {p.size}</span>
                    <span>Entry {p.entry_price}</span>
                    <span>Mark {p.mark_price}</span>
                    <span className={p.unrealized_pnl >= 0 ? 'positive' : 'negative'}>PnL {p.unrealized_pnl?.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            )}
            {activeTab === 'stats' && stats && (
              <div className="panel-section">
                <h3>Stats</h3>
                <div className="stats-grid">
                  <div className="stat"><div className="label">Total Trades</div><div className="value">{stats.total_trades}</div></div>
                  <div className="stat"><div className="label">Wins</div><div className="value positive">{stats.wins}</div></div>
                  <div className="stat"><div className="label">Losses</div><div className="value negative">{stats.losses}</div></div>
                  <div className="stat"><div className="label">Avg PnL</div><div className="value">{stats.avg_pnl}</div></div>
                  <div className="stat"><div className="label">Max Win</div><div className="value positive">{stats.max_win}</div></div>
                  <div className="stat"><div className="label">Max Loss</div><div className="value negative">{stats.max_loss}</div></div>
                  <div className="stat"><div className="label">Avg R</div><div className="value">{stats.avg_r}</div></div>
                  <div className="stat"><div className="label">Max R</div><div className="value positive">{stats.max_r}</div></div>
                  <div className="stat"><div className="label">Min R</div><div className="value negative">{stats.min_r}</div></div>
                </div>
              </div>
            )}
            {activeTab === 'trades' && (
              <div className="panel-section">
                <h3>Trades log</h3>
                <div className="log-list">{tradesLog.length ? tradesLog.map((line, i) => <div key={i} className="line">{line}</div>) : <span className="muted">No entries today</span>}</div>
              </div>
            )}
            {activeTab === 'trailing' && (
              <div className="panel-section">
                <h3>Trailing log</h3>
                <div className="log-list">{trailingLog.length ? trailingLog.map((line, i) => <div key={i} className="line">{line}</div>) : <span className="muted">No entries today</span>}</div>
              </div>
            )}
            {activeTab === 'signals' && (
              <div className="panel-section">
                <h3>Signals log</h3>
                <div className="log-list">{signalsLog.length ? signalsLog.map((line, i) => <div key={i} className="line">{line}</div>) : <span className="muted">No entries today</span>}</div>
              </div>
            )}
            {activeTab === 'settings' && <SettingsPanel />}
          </div>
        </div>
      </div>
    </div>
  );
}
