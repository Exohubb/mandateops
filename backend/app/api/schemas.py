"""Pydantic request/response models for the API layer."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RunBatchRequest(BaseModel):
    cohort_size: int = Field(default=50, ge=10, le=20000)
    seed: int = Field(default=2026)


class RunBatchResponse(BaseModel):
    batch_id: str
    status: str
    ai_enrichment_status: str = "pending"


class CopilotHistoryTurn(BaseModel):
    """One prior turn in the Ask Nira chat, sent back by the frontend so
    short follow-ups ("why?", "see it") can be resolved against what was
    just discussed. The frontend already holds this in its own chat state
    — the backend never persists it server-side.
    """

    role: str = Field(pattern="^(user|nira)$")
    text: str = Field(min_length=1, max_length=2000)


class CopilotQuestionRequest(BaseModel):
    batch_id: str
    question: str = Field(min_length=1, max_length=500)
    history: list[CopilotHistoryTurn] = Field(default_factory=list, max_length=12)


class VerifyChainResponse(BaseModel):
    batch_id: str
    valid: bool
    total_events: int
    first_invalid_sequence: int | None = None
