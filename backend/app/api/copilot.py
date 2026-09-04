"""AI Copilot ("Ask Nira") endpoint — grounded Q&A over one batch run's data.

Per BUILD-BLUEPRINT.md section 5.2 (Job #3): the backend retrieves the
relevant aggregates from SQLite FIRST, then hands them to Gemini as the
only source of truth. Gemini never sees the raw database — only the
specific numbers this endpoint decides are relevant.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.ai.gemini_client import ask_copilot
from app.api.schemas import CopilotQuestionRequest
from app.db.connection import get_db
from app.db import repository

router = APIRouter(prefix="/api/copilot", tags=["copilot"])


async def _build_grounded_context(conn, batch_id: str) -> dict:
    """Assemble the bounded set of data Nira is allowed to reason over for
    a given batch: the two strategy summaries, plus small per-bank
    aggregates computed in SQL (not sent as raw row dumps).
    """
    batch = await repository.get_batch_run(conn, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")

    mandateops_outcomes = await repository.get_outcomes(
        conn, batch_id=batch_id, strategy="mandateops", limit=20000
    )
    naive_outcomes = await repository.get_outcomes(
        conn, batch_id=batch_id, strategy="naive", limit=20000
    )

    def _bank_breakdown(outcomes: list[dict]) -> dict:
        breakdown: dict[str, dict] = {}
        for o in outcomes:
            b = breakdown.setdefault(o["bank"], {"total": 0, "recovered": 0})
            b["total"] += 1
            b["recovered"] += 1 if o["recovered"] else 0
        for bank, stats in breakdown.items():
            stats["recovery_rate"] = round(stats["recovered"] / stats["total"], 4) if stats["total"] else 0
        return breakdown

    def _state_breakdown(outcomes: list[dict]) -> dict:
        breakdown: dict[str, int] = {}
        for o in outcomes:
            breakdown[o["final_state"]] = breakdown.get(o["final_state"], 0) + 1
        return breakdown

    return {
        "batch_id": batch_id,
        "naive_summary": batch.get("naive_summary"),
        "mandateops_summary": batch.get("mandateops_summary"),
        "mandateops_bank_breakdown": _bank_breakdown(mandateops_outcomes),
        "naive_bank_breakdown": _bank_breakdown(naive_outcomes),
        "mandateops_final_state_breakdown": _state_breakdown(mandateops_outcomes),
    }


@router.post("/ask")
async def ask(request: CopilotQuestionRequest):
    conn = get_db()
    context = await _build_grounded_context(conn, request.batch_id)
    result = await ask_copilot(question=request.question, grounded_context=context)
    return result
