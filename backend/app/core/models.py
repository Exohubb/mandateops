"""Domain models for the deterministic core.

These are plain dataclasses — no ORM, no DB coupling. app/db/ is responsible
for turning these into SQLite rows and back. Keeping the two separate means
the state machine and rules can be unit tested with zero database involved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.core.enums import CycleState, MandateStatus


@dataclass
class Mandate:
    """A UPI AutoPay mandate: the standing recurring-payment authorization
    between a subscriber and a merchant. Independent of any single billing
    cycle's attempt history.
    """

    id: str
    subscriber_name: str
    bank: str
    plan_amount_paise: int  # amount is always an integer (paise), never AI-generated
    status: MandateStatus
    created_at: datetime


@dataclass
class Cycle:
    """One billing cycle's recovery process for a given mandate.

    `attempts_used` and `state` are the scarce-resource ledger at the heart
    of the whole product. cycle_number increases each billing period.
    """

    id: str
    mandate_id: str
    cycle_number: int
    state: CycleState
    attempts_used: int = 0
    notification_sent_at: datetime | None = None
    recovered_amount_paise: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Attempt:
    """A single executed (or suppressed) debit attempt within a cycle.

    attempt_number is 1-indexed and bounded by MAX_ATTEMPTS_PER_CYCLE.
    `scored_slot_probability` is filled in by the statistical layer, never AI.
    """

    id: str
    cycle_id: str
    attempt_number: int
    scheduled_for: datetime
    outcome: str  # AttemptOutcome value, stored as str for simple persistence
    decline_reason_raw: str | None = None
    decline_category: str | None = None  # DeclineCategory value
    classified_by: str | None = None  # ClassifiedBy value
    scored_slot_probability: float | None = None
    executed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AuditEvent:
    """One row of the hash-chained, append-only audit log.

    `prev_hash` is the hash of the previous event in the chain (or a fixed
    genesis value for the first event). `this_hash` is computed over the
    event's own content + prev_hash, so any tampering with an earlier row
    invalidates every hash after it — verifiable client-side with the
    "Verify Chain Integrity" button described in the blueprint.
    """

    id: str
    sequence: int
    timestamp: datetime
    actor_layer: str  # ActorLayer value
    event_type: str
    mandate_id: str | None
    cycle_id: str | None
    detail: dict
    prev_hash: str
    this_hash: str
