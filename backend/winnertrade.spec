# PyInstaller spec - WinnerTrade backend tek exe
# Çalıştırma: cd backend && pyinstaller winnertrade.spec

# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

# Uvicorn/FastAPI dinamik import'ları
uvicorn_imports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.loops.asyncio',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.wsproto_impl',
    'uvicorn.protocols.websockets_impl',
    'uvicorn.lifespan',
    'uvicorn.lifespan.off',
    'uvicorn.lifespan.on',
]

app_imports = [
    'api',
    'api.main',
    'api.routes',
    'api.routes.config',
    'api.routes.dashboard',
    'api.routes.engine_control',
    'core',
    'core.config_manager',
    'core.config_schema',
    'core.paths',
    'core.state',
    'core.logger',
    'storage',
    'storage.config_storage',
    'exchanges',
    'exchanges.factory',
    'exchanges.base_exchange',
    'exchanges.binance_futures',
    'exchanges.mexc_futures',
    'exchanges.paper_trader',
    'strategy',
    'strategy.indicators',
    'strategy.signal_generator',
    'strategy.trend_filter',
    'risk',
    'risk.risk_manager',
    'execution',
    'execution.order_executor',
    'execution.trailing_stop',
    'stats',
    'stats.statistics',
    'stats.trade_logger',
    'engine',
    'engine.loop',
    'utils',
    'utils.telegram',
]

a = Analysis(
    ['run_api.py'],
    pathex=['src'],
    binaries=[],
    datas=[('src', '')],
    hiddenimports=uvicorn_imports + app_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['talib', 'TA-Lib'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='winnertrade-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements=None,
)
