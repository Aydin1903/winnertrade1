# 🚀 WinnerTrade - Professional Trading Bot System

## 📋 Proje Hakkında

WinnerTrade, borsalarda (Binance, MEXC vb.) Futures işlemleri yapabilen, paper trade ve real trade destekleyen, risk yönetimi olan profesyonel bir trading bot sistemidir.

## 🏗️ Mimari Yapı

```
winnertrade/
├── backend/              # Python backend (FastAPI)
│   ├── src/
│   │   ├── core/        # Çekirdek modüller
│   │   ├── exchanges/   # Exchange connector'lar
│   │   ├── strategy/    # Trading stratejisi
│   │   ├── risk/        # Risk yönetimi
│   │   ├── stats/       # İstatistik sistemi
│   │   └── utils/       # Yardımcı fonksiyonlar
│   ├── config/          # Config dosyaları
│   ├── logs/            # Log dosyaları
│   └── requirements.txt
├── frontend/            # Electron + React frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── config/              # Ana config dosyası
└── docs/                # Dokümantasyon
```

## 🎯 Özellikler

- ✅ Paper Trade + Real Trade desteği
- ✅ Risk yönetimi (%1 risk, günlük -3R limiti)
- ✅ GUI ile izleme ve kontrol
- ✅ Detaylı istatistik ve log sistemi
- ✅ Top 10 coin (hacimsel) otomatik tespit
- ✅ Modüler ve genişletilebilir yapı

## 📦 Kurulum

Detaylar için [KURULUM.md](docs/KURULUM.md) dosyasına bakın.

**Nasıl test ederim?** → [TEST.md](docs/TEST.md) (geliştirme, backend exe, tam build).

**Installer’ı Python kurmadan nasıl üretirim?** → [DAGITIM.md](docs/DAGITIM.md): GitHub Actions ile (önerilen) veya hazır backend exe + `build-windows-npm-only.bat` (sadece Node.js).  
**GitHub’ı bilmiyorum, adım adım ne yapacağım?** → [GITHUB-ADIM-ADIM.md](docs/GITHUB-ADIM-ADIM.md).

## 🖥️ Çalıştırma

1. **Config:** `config/config.example.json` → `config/config.json` (API key vb. doldur).
2. **Tek tıkla (önerilen):** `cd frontend` → `npm install` → `npm run electron:dev`. Electron açılınca backend yoksa otomatik başlatır (Python PATH’te olmalı).
3. **İstersen ayrı ayrı:** Backend: `cd backend`, `set PYTHONPATH=src`, `uvicorn api.main:app --port 8000`. Frontend: `cd frontend`, `npm run dev` (tarayıcı) veya `npm run electron:dev` (masaüstü).

4. **Trading engine:** GUI’de “Start Engine” ile başlatılır (API üzerinden aynı process’te thread). İstersen ayrı terminalde `python -m engine` da çalıştırılabilir. Semboller: config’te `symbols.manual_list` doluysa o, boşsa ve `auto_detect_top_10: true` ise borsadan hacimsel top 10 USDT kullanılır.

5. **Telegram (isteğe bağlı, varsayılan kapalı):** Uygulama zaten otomatik işlem açtığı için şu an gerek yok. İleride “işlem açıldı/kapandı” bildirimi almak istersen config’te `telegram.enabled: true`, `bot_token` ve `chat_id` doldurman yeterli.

## 🔧 Geliştirme

Detaylar için [GELISTIRME.md](docs/GELISTIRME.md) dosyasına bakın.
