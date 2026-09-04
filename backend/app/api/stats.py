"""Retry-slot heatmap and the "How We Use AI" static-fact endpoint.

The AI-boundary table itself lives here as data (not just frontend copy)
so the frontend can render BUILD-BLUEPRINT.md section 6.7's table from a
single source of truth instead of duplicating it in JSX.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.enums import DeclineCategory
from app.simulation.orchestrator import heatmap_data

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/heatmap/{decline_category}")
async def get_heatmap(decline_category: str):
    valid_categories = {c.value for c in DeclineCategory}
    if decline_category not in valid_categories:
        decline_category = DeclineCategory.INSUFFICIENT_FUNDS.value
    return heatmap_data(decline_category)


AI_JUDGMENT_TABLE = [
    {
        "decision": "Whether a mandate is retried",
        "made_by": "Deterministic state machine",
        "why": "Legally and financially consequential — must be 100% reproducible",
    },
    {
        "decision": "Which time slot to use",
        "made_by": "Statistical scorer (empirical Bayes)",
        "why": "Inspectable math, not a black box, reports its own confidence",
    },
    {
        "decision": "What a messy bank decline string means",
        "made_by": "Nira (Gemini)",
        "why": "Free text has no fixed schema — exactly what LLMs are good at",
    },
    {
        "decision": "What to say to the customer",
        "made_by": "Nira (Gemini), from approved templates only",
        "why": "Tone and language variation, zero financial authority",
    },
    {
        "decision": "Answering a human's question about the batch",
        "made_by": "Nira (Gemini), grounded in this run's data only",
        "why": "Judgment lives in retrieval-then-explain, not decision-making",
    },
    {
        "decision": "Whether Gemini being down changes any of the above",
        "made_by": "No — deterministic fallback takes over, tagged transparently",
        "why": "AI availability must never be a single point of failure for money movement",
    },
]


@router.get("/ai-judgment-table")
async def get_ai_judgment_table():
    return AI_JUDGMENT_TABLE
