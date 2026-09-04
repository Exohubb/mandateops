"""Audit trail endpoints: the hash-chained event log + client-triggerable
chain verification (the "Verify Chain Integrity" button from
BUILD-BLUEPRINT.md section 6.6).
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas import VerifyChainResponse
from app.core.audit import verify_chain
from app.db.connection import get_db
from app.db import repository

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/{batch_id}")
async def get_audit_trail(batch_id: str, limit: int = 500):
    conn = get_db()
    events = await repository.get_audit_events(conn, batch_id)
    events = events[:limit]
    return [
        {
            "id": e.id,
            "sequence": e.sequence,
            "timestamp": e.timestamp.isoformat(),
            "actor_layer": e.actor_layer,
            "event_type": e.event_type,
            "mandate_id": e.mandate_id,
            "cycle_id": e.cycle_id,
            "detail": e.detail,
            "prev_hash": e.prev_hash,
            "this_hash": e.this_hash,
        }
        for e in events
    ]


@router.post("/{batch_id}/verify", response_model=VerifyChainResponse)
async def verify_audit_chain(batch_id: str) -> VerifyChainResponse:
    conn = get_db()
    events = await repository.get_audit_events(conn, batch_id)
    valid, bad_sequence = verify_chain(events)
    return VerifyChainResponse(
        batch_id=batch_id,
        valid=valid,
        total_events=len(events),
        first_invalid_sequence=bad_sequence,
    )
