"""Unit tests for app.core.engine.evaluate_cycle — the deterministic
decision function. These tests directly encode the two headline
failure-recovery demo scenarios from BUILD-BLUEPRINT.md:

  1. Mandate revoked mid-cycle with attempts remaining -> budget freezes.
  2. No notification sent yet -> attempt is suppressed, never scheduled.
"""

from datetime import datetime, timedelta

from app.core.enums import CycleState, DecisionType, MandateStatus
from app.core.models import Cycle, Mandate
from app.core.engine import evaluate_cycle, idempotency_key
from app.core.rules import is_non_peak


def _mandate(status: MandateStatus = MandateStatus.ACTIVE) -> Mandate:
    return Mandate(
        id="mandate-1",
        subscriber_name="Test Subscriber",
        bank="HDFC",
        plan_amount_paise=49900,
        status=status,
        created_at=datetime(2026, 1, 1),
    )


def _cycle(**overrides) -> Cycle:
    defaults = dict(
        id="cycle-1",
        mandate_id="mandate-1",
        cycle_number=1,
        state=CycleState.PENDING,
        attempts_used=0,
        notification_sent_at=None,
        recovered_amount_paise=0,
        created_at=datetime(2026, 1, 1),
    )
    defaults.update(overrides)
    return Cycle(**defaults)


def test_revoked_mandate_freezes_remaining_budget() -> None:
    """The headline failure-recovery scenario: revocation mid-cycle must
    freeze the budget rather than burn a guaranteed-failing attempt.
    """
    mandate = _mandate(status=MandateStatus.REVOKED)
    cycle = _cycle(attempts_used=2, state=CycleState.PENDING)
    now = datetime(2026, 1, 5, 6, 0)

    decision = evaluate_cycle(mandate=mandate, cycle=cycle, now=now)

    assert decision.decision_type == DecisionType.FREEZE_REVOKED
    assert decision.scheduled_for is None
    assert "2 attempt(s) saved" in decision.reason


def test_revoked_mandate_on_already_recovered_cycle_is_moot() -> None:
    mandate = _mandate(status=MandateStatus.REVOKED)
    cycle = _cycle(attempts_used=1, state=CycleState.RECOVERED)
    now = datetime(2026, 1, 5, 6, 0)

    decision = evaluate_cycle(mandate=mandate, cycle=cycle, now=now)

    assert decision.decision_type == DecisionType.TERMINAL_NO_ACTION


def test_paused_mandate_blocks_scheduling() -> None:
    mandate = _mandate(status=MandateStatus.PAUSED)
    cycle = _cycle(attempts_used=0)
    now = datetime(2026, 1, 5, 6, 0)

    decision = evaluate_cycle(mandate=mandate, cycle=cycle, now=now)

    assert decision.decision_type == DecisionType.FREEZE_PAUSED


def test_already_recovered_cycle_needs_no_action() -> None:
    mandate = _mandate()
    cycle = _cycle(state=CycleState.RECOVERED, attempts_used=1)
    now = datetime(2026, 1, 5, 6, 0)

    decision = evaluate_cycle(mandate=mandate, cycle=cycle, now=now)

    assert decision.decision_type == DecisionType.ALREADY_RECOVERED


def test_exhausted_budget_is_terminal() -> None:
    mandate = _mandate()
    cycle = _cycle(attempts_used=4, notification_sent_at=datetime(2026, 1, 3))
    now = datetime(2026, 1, 5, 6, 0)

    decision = evaluate_cycle(mandate=mandate, cycle=cycle, now=now)

    assert decision.decision_type == DecisionType.EXHAUSTED


def test_missing_notification_suppresses_scheduling() -> None:
    """Second failure-recovery scenario: no notification sent yet -> the
    scheduler must refuse to propose any attempt time at all.
    """
    mandate = _mandate()
    cycle = _cycle(attempts_used=0, notification_sent_at=None)
    now = datetime(2026, 1, 5, 6, 0)

    decision = evaluate_cycle(mandate=mandate, cycle=cycle, now=now)

    assert decision.decision_type == DecisionType.SUPPRESS_NOTIFICATION_MISSING
    assert decision.scheduled_for is None


def test_schedules_attempt_when_all_conditions_met() -> None:
    mandate = _mandate()
    notification_sent_at = datetime(2026, 1, 4, 5, 0)  # >24h before now
    cycle = _cycle(attempts_used=0, notification_sent_at=notification_sent_at)
    now = datetime(2026, 1, 5, 6, 0)  # non-peak hour

    decision = evaluate_cycle(mandate=mandate, cycle=cycle, now=now)

    assert decision.decision_type == DecisionType.SCHEDULE_ATTEMPT
    assert decision.scheduled_for is not None
    assert is_non_peak(decision.scheduled_for) is True
    assert decision.scheduled_for >= notification_sent_at + timedelta(hours=24)


def test_schedules_into_next_non_peak_window_if_earliest_time_is_peak() -> None:
    mandate = _mandate()
    # Notification satisfies lead time well before `now`, but `now` itself
    # is a peak hour -> engine must roll forward to the next non-peak slot.
    notification_sent_at = datetime(2026, 1, 3, 0, 0)
    cycle = _cycle(attempts_used=0, notification_sent_at=notification_sent_at)
    now = datetime(2026, 1, 5, 11, 0)  # peak hour (10:00-13:00 blocked)

    decision = evaluate_cycle(mandate=mandate, cycle=cycle, now=now)

    assert decision.decision_type == DecisionType.SCHEDULE_ATTEMPT
    assert is_non_peak(decision.scheduled_for) is True
    assert decision.scheduled_for >= now


def test_idempotency_key_is_stable_and_unique_per_attempt() -> None:
    key1 = idempotency_key("mandate-1", 1, 1)
    key2 = idempotency_key("mandate-1", 1, 2)
    key3 = idempotency_key("mandate-1", 1, 1)

    assert key1 != key2
    assert key1 == key3
    assert key1 == "mandate-1:1:1"
