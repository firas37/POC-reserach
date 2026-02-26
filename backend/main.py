"""
Zyga Research & Enrichment Agent — FastAPI Application
Entry point: uvicorn backend.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from backend.api.routes import router

# ── App ──────────────────────────────────────────────────────
app = FastAPI(
    title="Zyga Research & Enrichment PoC",
    description="AI-powered B2B prospect research and enrichment agent",
    version="0.1.0",
)

# ── CORS (allow all origins for local development) ───────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API routes at /api ───────────────────────────────────────
app.include_router(router, prefix="/api")

# ── Serve frontend static files ─────────────────────────────
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
