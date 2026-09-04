"""FastAPI application entrypoint.

Run locally with: uv run uvicorn app.main:app --reload --port 8000

In production, this same process also serves the built frontend
(frontend/dist) as static files, so the whole app — API and UI — runs as
one process on one port. This keeps deployment to a single-service, no
extra reverse-proxy-config-for-a-second-app footprint, which matters on a
shared box already running another team's service.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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


# --- Serve the built frontend (production only) --------------------------
# Resolved relative to this file so it works regardless of the working
# directory uvicorn was launched from. Silently skipped if the frontend
# hasn't been built (e.g. local dev, where Vite's own dev server handles
# the UI instead) — every API route above is registered first, so this
# never shadows them.
_FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if _FRONTEND_DIST.is_dir():
    app.mount(
        "/assets", StaticFiles(directory=_FRONTEND_DIST / "assets"), name="assets"
    )

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Catch-all for the SPA: any path that isn't an /api/* or /assets/*
        route (already matched above) falls through to index.html, so
        client-side routing (React Router) works on a hard refresh/direct
        link to e.g. /dashboard instead of 404ing.
        """
        candidate = _FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_FRONTEND_DIST / "index.html")
