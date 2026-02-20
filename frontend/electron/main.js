const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

const API_PORT = 8000;
const API_HEALTH = `http://127.0.0.1:${API_PORT}/health`;
const BACKEND_EXE_NAME = 'winnertrade-backend.exe';
let backendProcess = null;

function getBackendPath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'backend');
  }
  return path.join(__dirname, '..', '..', 'backend');
}

function getBackendExePath() {
  return path.join(process.resourcesPath, 'backend', BACKEND_EXE_NAME);
}

function checkBackendReady() {
  return new Promise((resolve) => {
    const req = http.get(API_HEALTH, (res) => {
      let data = '';
      res.on('data', (ch) => { data += ch; });
      res.on('end', () => resolve(res.statusCode === 200));
    });
    req.on('error', () => resolve(false));
    req.setTimeout(2000, () => { req.destroy(); resolve(false); });
  });
}

function waitForBackend(maxWaitMs = 30000) {
  return new Promise((resolve) => {
    const start = Date.now();
    const tryOnce = () => {
      checkBackendReady().then((ok) => {
        if (ok) return resolve(true);
        if (Date.now() - start >= maxWaitMs) return resolve(false);
        setTimeout(tryOnce, 500);
      });
    };
    tryOnce();
  });
}

function startBackend() {
  if (app.isPackaged && process.platform === 'win32') {
    const exePath = getBackendExePath();
    backendProcess = spawn(exePath, [], {
      cwd: path.dirname(exePath),
      stdio: 'ignore',
      windowsHide: true,
    });
  } else {
    const backendDir = getBackendPath();
    const srcPath = path.join(backendDir, 'src');
    const env = { ...process.env, PYTHONPATH: srcPath };
    const py = process.platform === 'win32' ? 'python' : 'python3';
    backendProcess = spawn(py, ['-m', 'uvicorn', 'api.main:app', '--port', String(API_PORT)], {
      cwd: backendDir,
      env,
      stdio: 'ignore',
    });
  }
  backendProcess.on('error', () => { backendProcess = null; });
  backendProcess.on('exit', (code) => { backendProcess = null; });
}

function ensureBackendThenCreateWindow() {
  checkBackendReady().then((ready) => {
    if (ready) {
      createWindow();
      return;
    }
    startBackend();
    waitForBackend().then((ok) => {
      if (ok) createWindow();
      else createWindow();
    });
  });
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: { nodeIntegration: false, contextIsolation: true },
  });
  const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
  if (isDev) {
    win.loadURL('http://localhost:5173');
    win.webContents.openDevTools();
  } else {
    win.loadFile(path.join(__dirname, '../dist/index.html'));
  }
}

app.whenReady().then(ensureBackendThenCreateWindow);

app.on('window-all-closed', () => {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) ensureBackendThenCreateWindow();
});

app.on('before-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
});
