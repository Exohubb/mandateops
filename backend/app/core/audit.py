"""Hash-chained, append-only audit log.

Every decision the system makes — deterministic, statistical, or AI — is
written here through `build_event`. Each event's hash covers its own
content plus the previous event's hash, so the chain can be verified end to
end: tamper with row 500 and every hash from 500 onward stops matching.

This module is pure (no DB, no I/O) — app/db/repository.py is responsible
for persisting AuditEvent rows and reading them back in sequence order.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from app.core.models import AuditEvent

GENESIS_HASH = "0" * 64


def _canonical_json(detail: dict) -> str:
    """Stable JSON serialization so identical detail dicts always hash the
    same way regardless of key insertion order.
    """
    return json.dumps(detail, sort_keys=True, separators=(",", ":"), default=str)


def compute_hash(
    *,
    sequence: int,
    timestamp: datetime,
    actor_layer: str,
    event_type: str,
    mandate_id: str | None,
    cycle_id: str | None,
    detail: dict,
    prev_hash: str,
) -> str:
    """Deterministic SHA-256 hash over an event's full content + prev_hash.

    Deliberately excludes the event's own id/hash (nothing hashes itself).
    """
    payload = "|".join(
        [
            str(sequence),
            timestamp.isoformat(),
            actor_layer,
            event_type,
            mandate_id or "",
            cycle_id or "",
            _canonical_json(detail),
            prev_hash,
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_event(
    *,
    event_id: str,
    sequence: int,
    actor_layer: str,
    event_type: str,
    mandate_id: str | None,
    cycle_id: str | None,
    detail: dict,
    prev_hash: str,
    timestamp: datetime | None = None,
) -> AuditEvent:
    """Construct the next AuditEvent in the chain, given the previous event's
    hash. Caller (the repository layer) is responsible for looking up
    `prev_hash` (GENESIS_HASH if this is the very first event) and persisting
    the result.
    """
    ts = timestamp or datetime.now(timezone.utc)
    this_hash = compute_hash(
        sequence=sequence,
        timestamp=ts,
        actor_layer=actor_layer,
        event_type=event_type,
        mandate_id=mandate_id,
        cycle_id=cycle_id,
        detail=detail,
        prev_hash=prev_hash,
    )
    return AuditEvent(
        id=event_id,
        sequence=sequence,
        timestamp=ts,
        actor_layer=actor_layer,
        event_type=event_type,
        mandate_id=mandate_id,
        cycle_id=cycle_id,
        detail=detail,
        prev_hash=prev_hash,
        this_hash=this_hash,
    )


def verify_chain(events: list[AuditEvent]) -> tuple[bool, int | None]:
    """Recompute every hash in `events` (assumed already sorted by sequence
    ascending) and confirm the chain is intact.

    Returns (True, None) if the whole chain verifies, or (False, sequence)
    naming the first sequence number where verification failed.
    """
    expected_prev = GENESIS_HASH
    for event in events:
        if event.prev_hash != expected_prev:
            return False, event.sequence
        recomputed = compute_hash(
            sequence=event.sequence,
            timestamp=event.timestamp,
            actor_layer=event.actor_layer,
            event_type=event.event_type,
            mandate_id=event.mandate_id,
            cycle_id=event.cycle_id,
            detail=event.detail,
            prev_hash=event.prev_hash,
        )
        if recomputed != event.this_hash:
            return False, event.sequence
        expected_prev = event.this_hash
    return True, None
