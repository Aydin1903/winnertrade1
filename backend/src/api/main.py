"""
FastAPI uygulaması - GUI ve dış entegrasyon için REST API.

Çalıştırma (backend klasöründen, PYTHONPATH=src):
  uvicorn api.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import config as config_routes
from .routes import dashboard, engine_control

app = FastAPI(title="WinnerTrade API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(config_routes.router, prefix="/api", tags=["config"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(engine_control.router, prefix="/api", tags=["engine"])

@app.get("/health")
def health():
    return {"status": "ok"}
