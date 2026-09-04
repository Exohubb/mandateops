"""Batch run endpoints: kick off a run, inspect its status and summary."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.schemas import RunBatchRequest, RunBatchResponse
from app.db.connection import get_db
from app.db import repository
from app.simulation.orchestrator import run_batch

router = APIRouter(prefix="/api/batches", tags=["batches"])


@router.post("", response_model=RunBatchResponse)
async def create_batch(request: RunBatchRequest) -> RunBatchResponse:
    conn = get_db()
    batch_id = await run_batch(conn, cohort_size=request.cohort_size, seed=request.seed)
    return RunBatchResponse(batch_id=batch_id, status="completed", ai_enrichment_status="pending")


@router.get("")
async def list_batches(limit: int = 20):
    conn = get_db()
    return await repository.list_batch_runs(conn, limit=limit)


@router.get("/{batch_id}")
async def get_batch(batch_id: str):
    conn = get_db()
    batch = await repository.get_batch_run(conn, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.get("/{batch_id}/outcomes/{strategy}")
async def get_outcomes(batch_id: str, strategy: str, limit: int = 500, offset: int = 0):
    if strategy not in ("naive", "mandateops"):
        raise HTTPException(status_code=400, detail="strategy must be 'naive' or 'mandateops'")
    conn = get_db()
    return await repository.get_outcomes(
        conn, batch_id=batch_id, strategy=strategy, limit=limit, offset=offset
    )


@router.get("/{batch_id}/mandate/{mandate_id}")
async def get_mandate_detail(batch_id: str, mandate_id: str):
    conn = get_db()
    naive = await repository.get_outcome_by_mandate(
        conn, batch_id=batch_id, strategy="naive", mandate_id=mandate_id
    )
    mandateops = await repository.get_outcome_by_mandate(
        conn, batch_id=batch_id, strategy="mandateops", mandate_id=mandate_id
    )
    if naive is None and mandateops is None:
        raise HTTPException(status_code=404, detail="Mandate not found in this batch")
    events = await repository.get_simulation_events(
        conn, batch_id=batch_id, mandate_id=mandate_id, limit=50
    )
    return {"naive": naive, "mandateops": mandateops, "events": events}


@router.get("/{batch_id}/events/{strategy}")
async def get_events(batch_id: str, strategy: str, limit: int = 200):
    if strategy not in ("naive", "mandateops"):
        raise HTTPException(status_code=400, detail="strategy must be 'naive' or 'mandateops'")
    conn = get_db()
    return await repository.get_simulation_events(
        conn, batch_id=batch_id, strategy=strategy, limit=limit
    )


@router.delete("/{batch_id}")
async def delete_batch(batch_id: str):
    conn = get_db()
    deleted = await repository.delete_batch_run(conn, batch_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Batch not found")
    return {"batch_id": batch_id, "deleted": True}
