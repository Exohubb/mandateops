"""The Naive-vs-MandateOps batch simulation runner.

This module is the entire "3-minute demo WOW factor" from
BUILD-BLUEPRINT.md section 6.3, computed analytically rather than by
ticking through every simulated hour: for each mandate cycle we can
determine exactly what each strategy does and when, because both
strategies are deterministic policies over a small state space.

Two strategies, run over the SAME cohort and the SAME ground-truth outcome
model (app.simulation.ground_truth), so any difference in recovered rupees
is attributable purely to scheduling policy, not to luck:

  - `run_naive`: models Razorpay's default behavior as described in
    BUILD-BLUEPRINT.md — "we automatically retry the payment on the
    following day." It ignores mandate status (retries a revoked/paused
    mandate blindly), ignores non-peak windows, and ignores the
    notification precondition. It simply retries once every 24h until the
    4-attempt budget is exhausted or a retry succeeds.

  - `run_mandateops`: uses app.core.engine.evaluate_cycle for every
    eligibility decision (so it can never violate a compliance clause) and
    app.statistical.scorer.RetrySlotScorer to pick WHICH legal hour-of-day
    to use for each attempt, rather than just the earliest one.

Both strategies produce a BatchResult with per-mandate outcomes, aggregate
totals, and a list of SimulationEvent for the live event feed / audit log.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.core.enums import ActorLayer, CycleState, DecisionType, MandateStatus
from app.core.engine import evaluate_cycle
from app.core.rules import MAX_ATTEMPTS_PER_CYCLE
from app.simulation.cohort import SyntheticCycleRecord
from app.simulation.events import SimulationEvent
from app.simulation.ground_truth import draw_outcome
from app.statistical.scorer import RetrySlotScorer


@dataclass
class MandateOutcome:
    """The final result of running one strategy against one mandate cycle."""

    mandate_id: str
    cycle_id: str
    bank: str
    decline_category: str
    final_state: str  # CycleState value
    attempts_used: int
    attempts_saved: int
    recovered: bool
    recovered_amount_paise: int
    plan_amount_paise: int


@dataclass
class BatchResult:
    """Aggregate result of running one strategy over an entire cohort."""

    strategy_name: str
    outcomes: list[MandateOutcome] = field(default_factory=list)
    events: list[SimulationEvent] = field(default_factory=list)

    @property
    def total_mandates(self) -> int:
        return len(self.outcomes)

    @property
    def recovered_count(self) -> int:
        return sum(1 for o in self.outcomes if o.recovered)

    @property
    def recovered_rupees(self) -> float:
        return sum(o.recovered_amount_paise for o in self.outcomes) / 100.0

    @property
    def total_attempts_used(self) -> int:
        return sum(o.attempts_used for o in self.outcomes)

    @property
    def total_attempts_saved(self) -> int:
        return sum(o.attempts_saved for o in self.outcomes)

    def summary(self) -> dict:
        return {
            "strategy": self.strategy_name,
            "total_mandates": self.total_mandates,
            "recovered_count": self.recovered_count,
            "recovered_rupees": round(self.recovered_rupees, 2),
            "total_attempts_used": self.total_attempts_used,
            "total_attempts_saved": self.total_attempts_saved,
            "recovery_rate": round(self.recovered_count / self.total_mandates, 4)
            if self.total_mandates
            else 0.0,
        }


def _next_occurrence_of_hour(after: datetime, hour: int) -> datetime:
    """Earliest datetime >= `after` at the given hour, minute 30 (matching
    how app.statistical.constants.LEGAL_HOURS was derived — see that
    module's docstring for why minute 30 is used as the representative
    point-in-hour for legality checks).
    """
    candidate = after.replace(hour=hour, minute=30, second=0, microsecond=0)
    if candidate < after:
        candidate += timedelta(days=1)
    return candidate


# --- Naive strategy ---------------------------------------------------------


def run_naive(
    records: list[SyntheticCycleRecord], *, seed: int = 1
) -> BatchResult:
    """Razorpay-default baseline: retry once every 24h, up to the 4-attempt
    ceiling, ignoring mandate status, windows, and notification entirely.
    """
    rng = random.Random(seed)
    result = BatchResult(strategy_name="naive")

    for record in records:
        mandate = record.mandate
        cycle = record.cycle
        attempts_used = cycle.attempts_used  # already 1 (the initial failed attempt)
        recovered = False
        recovered_amount = 0
        attempt_time = cycle.created_at

        while attempts_used < MAX_ATTEMPTS_PER_CYCLE and not recovered:
            attempts_used += 1
            attempt_time = attempt_time + timedelta(days=1)
            success = draw_outcome(
                rng, mandate.bank, record.initial_decline_category, attempt_time.hour
            )
            result.events.append(
                SimulationEvent(
                    timestamp=attempt_time,
                    mandate_id=mandate.id,
                    cycle_id=cycle.id,
                    event_type="ATTEMPT_EXECUTED" if success else "ATTEMPT_FAILED",
                    actor_layer=ActorLayer.DETERMINISTIC.value,
                    detail={
                        "strategy": "naive",
                        "attempt_number": attempts_used,
                        "success": success,
                        "ignored_compliance": True,
                    },
                )
            )
            if success:
                recovered = True
                recovered_amount = mandate.plan_amount_paise

        result.outcomes.append(
            MandateOutcome(
                mandate_id=mandate.id,
                cycle_id=cycle.id,
                bank=mandate.bank,
                decline_category=record.initial_decline_category,
                final_state=(
                    CycleState.RECOVERED.value if recovered else CycleState.EXHAUSTED.value
                ),
                attempts_used=attempts_used,
                attempts_saved=0,  # naive never deliberately saves attempts
                recovered=recovered,
                recovered_amount_paise=recovered_amount,
                plan_amount_paise=mandate.plan_amount_paise,
            )
        )

    return result


# --- MandateOps strategy ----------------------------------------------------


def run_mandateops(
    records: list[SyntheticCycleRecord],
    scorer: RetrySlotScorer,
    *,
    seed: int = 1,
) -> BatchResult:
    """The constraint-aware strategy: every eligibility decision goes through
    evaluate_cycle; every scheduled attempt's hour-of-day is chosen by the
    statistical scorer among legally eligible hours.
    """
    rng = random.Random(seed)
    result = BatchResult(strategy_name="mandateops")

    for record in records:
        mandate = mandate_copy = record.mandate
        cycle = record.cycle
        category = record.initial_decline_category

        # Work on a mutable local copy of the fields evaluate_cycle reads,
        # since the shared record/mandate/cycle objects are reused across
        # both strategies and must not be mutated in place.
        current_status = mandate.status
        attempts_used = cycle.attempts_used
        state = cycle.state
        notification_sent_at: datetime | None = None if record.notification_send_fails else cycle.created_at
        recovered = False
        recovered_amount = 0
        now = cycle.created_at

        # Emit the notification-send event up front so it's visible in the
        # audit trail/event feed, including the deliberate failure case.
        if record.notification_send_fails:
            result.events.append(
                SimulationEvent(
                    timestamp=now,
                    mandate_id=mandate.id,
                    cycle_id=cycle.id,
                    event_type="NOTIFICATION_SEND_FAILED",
                    actor_layer=ActorLayer.DETERMINISTIC.value,
                    detail={"reason": "Notification provider error (simulated)"},
                )
            )
        else:
            result.events.append(
                SimulationEvent(
                    timestamp=now,
                    mandate_id=mandate.id,
                    cycle_id=cycle.id,
                    event_type="NOTIFICATION_SENT",
                    actor_layer=ActorLayer.DETERMINISTIC.value,
                    detail={"sent_at": now.isoformat()},
                )
            )

        # Bounded loop: at most MAX_ATTEMPTS_PER_CYCLE scheduling decisions,
        # plus the freeze/suppress/exhaust terminal decision.
        safety_counter = 0
        while safety_counter < MAX_ATTEMPTS_PER_CYCLE + 1:
            safety_counter += 1

            # Apply the mid-cycle revocation trigger: once attempts_used
            # reaches the configured threshold, flip status to REVOKED
            # before this decision — matching the headline demo scenario.
            if (
                record.mid_cycle_revocation_after is not None
                and attempts_used >= record.mid_cycle_revocation_after
                and current_status == MandateStatus.ACTIVE
            ):
                current_status = MandateStatus.REVOKED
                result.events.append(
                    SimulationEvent(
                        timestamp=now,
                        mandate_id=mandate.id,
                        cycle_id=cycle.id,
                        event_type="MANDATE_REVOKED_UPSTREAM",
                        actor_layer=ActorLayer.DETERMINISTIC.value,
                        detail={"attempts_used_at_revocation": attempts_used},
                    )
                )

            probe_mandate = mandate.__class__(
                id=mandate.id,
                subscriber_name=mandate.subscriber_name,
                bank=mandate.bank,
                plan_amount_paise=mandate.plan_amount_paise,
                status=current_status,
                created_at=mandate.created_at,
            )
            probe_cycle = cycle.__class__(
                id=cycle.id,
                mandate_id=cycle.mandate_id,
                cycle_number=cycle.cycle_number,
                state=state,
                attempts_used=attempts_used,
                notification_sent_at=notification_sent_at,
                recovered_amount_paise=recovered_amount,
                created_at=cycle.created_at,
            )

            decision = evaluate_cycle(mandate=probe_mandate, cycle=probe_cycle, now=now)

            if decision.decision_type == DecisionType.SCHEDULE_ATTEMPT:
                # Use the statistical scorer to pick the best LEGAL hour,
                # then find its next calendar occurrence at/after the
                # engine's earliest-eligible candidate time.
                best = scorer.best_legal_slot(mandate.bank, category)
                scheduled_time = _next_occurrence_of_hour(decision.scheduled_for, best.hour)

                attempts_used += 1
                now = scheduled_time
                success = draw_outcome(rng, mandate.bank, category, scheduled_time.hour)

                result.events.append(
                    SimulationEvent(
                        timestamp=scheduled_time,
                        mandate_id=mandate.id,
                        cycle_id=cycle.id,
                        event_type="ATTEMPT_EXECUTED" if success else "ATTEMPT_FAILED",
                        actor_layer=ActorLayer.STATISTICAL.value,
                        detail={
                            "strategy": "mandateops",
                            "attempt_number": attempts_used,
                            "success": success,
                            "scored_probability": best.shrunk_probability,
                            "sufficient_support": best.sufficient_support,
                        },
                    )
                )

                if success:
                    recovered = True
                    recovered_amount = mandate.plan_amount_paise
                    state = CycleState.RECOVERED
                    break
                # else loop again — will re-evaluate (possibly exhausted now)
                now = scheduled_time + timedelta(minutes=1)
                continue

            if decision.decision_type == DecisionType.FREEZE_REVOKED:
                state = CycleState.FROZEN_REVOKED
                result.events.append(
                    SimulationEvent(
                        timestamp=now,
                        mandate_id=mandate.id,
                        cycle_id=cycle.id,
                        event_type="ATTEMPT_BUDGET_FROZEN",
                        actor_layer=ActorLayer.DETERMINISTIC.value,
                        detail={"reason": decision.reason, "attempts_used": attempts_used},
                    )
                )
                break

            if decision.decision_type == DecisionType.FREEZE_PAUSED:
                state = CycleState.FROZEN_PAUSED
                result.events.append(
                    SimulationEvent(
                        timestamp=now,
                        mandate_id=mandate.id,
                        cycle_id=cycle.id,
                        event_type="ATTEMPT_BUDGET_FROZEN",
                        actor_layer=ActorLayer.DETERMINISTIC.value,
                        detail={"reason": decision.reason, "attempts_used": attempts_used},
                    )
                )
                break

            if decision.decision_type == DecisionType.SUPPRESS_NOTIFICATION_MISSING:
                state = CycleState.FROZEN_NOTIFICATION_FAILED
                result.events.append(
                    SimulationEvent(
                        timestamp=now,
                        mandate_id=mandate.id,
                        cycle_id=cycle.id,
                        event_type="ATTEMPT_SUPPRESSED",
                        actor_layer=ActorLayer.DETERMINISTIC.value,
                        detail={"reason": decision.reason},
                    )
                )
                break

            if decision.decision_type == DecisionType.EXHAUSTED:
                state = CycleState.EXHAUSTED
                result.events.append(
                    SimulationEvent(
                        timestamp=now,
                        mandate_id=mandate.id,
                        cycle_id=cycle.id,
                        event_type="ATTEMPT_BUDGET_EXHAUSTED",
                        actor_layer=ActorLayer.DETERMINISTIC.value,
                        detail={"reason": decision.reason},
                    )
                )
                break

            # ALREADY_RECOVERED / TERMINAL_NO_ACTION — nothing further to do.
            break

        attempts_saved = max(0, MAX_ATTEMPTS_PER_CYCLE - attempts_used) if not recovered and state in (
            CycleState.FROZEN_REVOKED,
            CycleState.FROZEN_PAUSED,
            CycleState.FROZEN_NOTIFICATION_FAILED,
        ) else 0

        result.outcomes.append(
            MandateOutcome(
                mandate_id=mandate.id,
                cycle_id=cycle.id,
                bank=mandate.bank,
                decline_category=category,
                final_state=state.value if hasattr(state, "value") else str(state),
                attempts_used=attempts_used,
                attempts_saved=attempts_saved,
                recovered=recovered,
                recovered_amount_paise=recovered_amount,
                plan_amount_paise=mandate.plan_amount_paise,
            )
        )

    return result
