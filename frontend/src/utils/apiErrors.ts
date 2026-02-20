/**
 * API hatalarını kullanıcı dostu Türkçe mesajlara çevirir.
 */

export function isNetworkError(e: unknown): boolean {
  if (e instanceof TypeError) return true;
  if (e instanceof Error) {
    const m = e.message.toLowerCase();
    return m === 'failed to fetch' || m.includes('load failed') || m.includes('networkerror') || m.includes('network request failed');
  }
  return false;
}

function getMessage(e: unknown): string {
  if (e instanceof Error) return e.message;
  return String(e);
}

/** Backend JSON hata gövdesinden detail alır (FastAPI formatı). */
function parseDetail(msg: string): string | null {
  try {
    const o = JSON.parse(msg);
    if (o && typeof o.detail === 'string') return o.detail;
  } catch {
    // ignore
  }
  return null;
}

/**
 * Genel API hataları için kullanıcı dostu mesaj.
 * Dashboard ve diğer ekranlarda kullanılır.
 */
export function toFriendlyApiError(e: unknown): string {
  if (isNetworkError(e)) {
    return "Backend'e bağlanılamıyor. Lütfen backend'in çalıştığından emin olun (örn. uvicorn api.main:app --port 8000).";
  }
  const msg = getMessage(e);
  const detail = parseDetail(msg);
  const text = detail ?? msg;
  return text || 'Bir hata oluştu.';
}

/**
 * Bağlantı testi (test-connection) ve config kaydetme hataları için.
 * "API key geçersiz" gibi net uyarılar üretir.
 */
export function toFriendlyConnectionError(e: unknown): string {
  if (isNetworkError(e)) {
    return "Backend'e bağlanılamıyor. Backend'in çalıştığından emin olun.";
  }
  const msg = getMessage(e);
  const detail = parseDetail(msg) ?? msg;
  const lower = detail.toLowerCase();
  if (
    lower.includes('invalid') ||
    lower.includes('api') && (lower.includes('key') || lower.includes('secret')) ||
    lower.includes('401') ||
    lower.includes('403') ||
    lower.includes('authentication') ||
    lower.includes('unauthorized') ||
    lower.includes('signature')
  ) {
    return 'API key veya secret geçersiz. Borsa panelinden anahtarlarınızı ve yetkileri kontrol edin.';
  }
  if (lower.includes('502') || lower.includes('bağlantı testi başarısız') || lower.includes('connection')) {
    return 'Borsa bağlantısı başarısız. API key, secret ve testnet ayarını kontrol edin.';
  }
  return detail || 'Bağlantı başarısız.';
}
