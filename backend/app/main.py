"""FastAPI application entrypoint.

Run locally with: uv run uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import audit, batches, copilot, live, stats
from app.config import get_settings
from app.db.connection import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="MandateOps API",
    description=(
        "Constraint-aware UPI AutoPay mandate retry sequencer — deterministic "
        "core, statistical retry-slot scorer, and a bounded Gemini AI layer "
        "(Nira). Built for the Razorpay Buildathon, Track 03."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(batches.router)
app.include_router(audit.router)
app.include_router(copilot.router)
app.include_router(stats.router)
app.include_router(live.router)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "gemini_configured": get_settings().gemini_configured,
    }
