"""Pydantic request/response models for the API layer."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RunBatchRequest(BaseModel):
    cohort_size: int = Field(default=5000, ge=10, le=20000)
    seed: int = Field(default=2026)


class RunBatchResponse(BaseModel):
    batch_id: str
    status: str


class CopilotQuestionRequest(BaseModel):
    batch_id: str
    question: str = Field(min_length=1, max_length=500)


class VerifyChainResponse(BaseModel):
    batch_id: str
    valid: bool
    total_events: int
    first_invalid_sequence: int | None = None
