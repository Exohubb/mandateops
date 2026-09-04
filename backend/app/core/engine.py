"""The deterministic decision engine.

`evaluate_cycle` is THE function that decides what happens next for a
mandate's billing cycle. It is pure, synchronous, and 100% reproducible:
same inputs always produce the same Decision. No AI, no randomness, no
wall-clock reads (the caller passes `now` explicitly) — this is what makes
replay possible and is the property the audit trail depends on.

Money never moves here. This module decides WHETHER and WHEN an attempt is
eligible; actually executing an attempt (calling out to a payment rail, or
in this project's case, the simulation engine) is a separate step.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.core.enums import CycleState, DecisionType, MandateStatus
from app.core.models import Cycle, Mandate
from app.core.rules import (
    MAX_ATTEMPTS_PER_CYCLE,
    MIN_NOTIFICATION_LEAD_TIME,
    check_attempt_eligibility,
    next_non_peak_slot,
)


@dataclass(frozen=True)
class Decision:
    """The outcome of evaluating one cycle at one point in time.

    `scheduled_for` is populated only for SCHEDULE_ATTEMPT (when to fire)
    and SUPPRESS_NOTIFICATION_MISSING (earliest time it could become
    eligible once a notification is sent). `reason` is a short, human and
    machine-readable string suitable for the audit log's `detail`.
    """

    decision_type: DecisionType
    scheduled_for: datetime | None
    reason: str


def idempotency_key(mandate_id: str, cycle_number: int, attempt_number: int) -> str:
    """Deterministic key so a webhook replay or a re-run of the same
    scheduling decision can never produce a duplicate attempt / double debit.
    """
    return f"{mandate_id}:{cycle_number}:{attempt_number}"


def evaluate_cycle(
    *,
    mandate: Mandate,
    cycle: Cycle,
    now: datetime,
) -> Decision:
    """Evaluate the current state of `cycle` (for `mandate`) as of `now` and
    return the single next Decision. Ordered checks, most authoritative
    (rail-side mandate state) first, so the reasoning is easy to read top to
    bottom and matches how a human compliance reviewer would reason about it.
    """

    # 1. Rail-side mandate state overrides everything — a revoked or paused
    #    mandate must never spend an attempt, regardless of budget remaining.
    if mandate.status == MandateStatus.REVOKED:
        if cycle.state in (CycleState.RECOVERED, CycleState.EXHAUSTED):
            return Decision(
                decision_type=DecisionType.TERMINAL_NO_ACTION,
                scheduled_for=None,
                reason="Cycle already terminal; revocation is moot.",
            )
        return Decision(
            decision_type=DecisionType.FREEZE_REVOKED,
            scheduled_for=None,
            reason=(
                "Mandate revoked upstream mid-cycle. Freezing remaining attempt "
                f"budget ({MAX_ATTEMPTS_PER_CYCLE - cycle.attempts_used} attempt(s) "
                "saved) instead of spending it on a guaranteed failure."
            ),
        )

    if mandate.status == MandateStatus.PAUSED:
        if cycle.state in (CycleState.RECOVERED, CycleState.EXHAUSTED):
            return Decision(
                decision_type=DecisionType.TERMINAL_NO_ACTION,
                scheduled_for=None,
                reason="Cycle already terminal; pause is moot.",
            )
        return Decision(
            decision_type=DecisionType.FREEZE_PAUSED,
            scheduled_for=None,
            reason="Mandate is paused. No attempt is eligible while paused.",
        )

    # 2. Cycle already resolved — nothing further to decide.
    if cycle.state == CycleState.RECOVERED:
        return Decision(
            decision_type=DecisionType.ALREADY_RECOVERED,
            scheduled_for=None,
            reason="Cycle already recovered; no further attempts needed.",
        )

    # 3. Attempt budget exhausted — hard stop, independent of anything else.
    if cycle.attempts_used >= MAX_ATTEMPTS_PER_CYCLE:
        return Decision(
            decision_type=DecisionType.EXHAUSTED,
            scheduled_for=None,
            reason=f"All {MAX_ATTEMPTS_PER_CYCLE} attempts used. Cycle exhausted.",
        )

    # 4. Notification precondition. A debit may never be scheduled unless a
    #    pre-debit notice was already sent >=24h before the proposed time.
    #    If no notification has gone out yet, we cannot schedule at all —
    #    surface that explicitly rather than silently picking a time anyway.
    if cycle.notification_sent_at is None:
        return Decision(
            decision_type=DecisionType.SUPPRESS_NOTIFICATION_MISSING,
            scheduled_for=None,
            reason=(
                "No pre-debit notification has been sent for this cycle. "
                "An attempt cannot be scheduled until a notification is sent "
                "and its 24-hour lead time has elapsed."
            ),
        )

    # 5. We have a notification timestamp — find the earliest non-peak slot
    #    that also satisfies the 24h lead time, then confirm it against the
    #    full compliance gate (belt-and-suspenders: rules.py is the single
    #    source of truth for eligibility, this function must never diverge
    #    from it).
    earliest_by_notification = cycle.notification_sent_at + MIN_NOTIFICATION_LEAD_TIME
    candidate_start = max(now, earliest_by_notification)
    candidate_slot = next_non_peak_slot(candidate_start)

    check = check_attempt_eligibility(
        attempts_used=cycle.attempts_used,
        attempt_time=candidate_slot,
        notification_sent_at=cycle.notification_sent_at,
    )
    if not check.passed:
        # Should be rare given the construction above, but if the gate still
        # rejects it, surface the exact failing clause rather than guessing.
        return Decision(
            decision_type=DecisionType.SUPPRESS_NOTIFICATION_MISSING,
            scheduled_for=None,
            reason=f"Compliance gate rejected candidate slot: {check.failing_clause}",
        )

    return Decision(
        decision_type=DecisionType.SCHEDULE_ATTEMPT,
        scheduled_for=candidate_slot,
        reason=(
            f"Attempt {cycle.attempts_used + 1}/{MAX_ATTEMPTS_PER_CYCLE} scheduled "
            f"for {candidate_slot.isoformat()} (non-peak window, notification lead "
            "time satisfied)."
        ),
    )
