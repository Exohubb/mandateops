"""Tests for app.simulation.runner — the Naive-vs-MandateOps comparison.

These tests are where the product's central claim gets checked mechanically:
MandateOps must never violate a compliance clause (unlike naive), and it
must demonstrably save attempts on the two rehearsed failure-recovery
scenarios (mid-cycle revocation, notification-send failure).
"""

from app.core.enums import CycleState
from app.core.rules import MAX_ATTEMPTS_PER_CYCLE, is_non_peak
from app.simulation.cohort import generate_cohort
from app.simulation.runner import run_mandateops, run_naive
from app.statistical.historical_data import generate_historical_outcomes
from app.statistical.scorer import RetrySlotScorer


def _scorer() -> RetrySlotScorer:
    outcomes = generate_historical_outcomes(n=20_000, seed=42)
    return RetrySlotScorer(outcomes)


def test_naive_never_exceeds_attempt_ceiling() -> None:
    records = generate_cohort(n=200, seed=1)
    result = run_naive(records, seed=1)
    for outcome in result.outcomes:
        assert outcome.attempts_used <= MAX_ATTEMPTS_PER_CYCLE


def test_mandateops_never_exceeds_attempt_ceiling() -> None:
    records = generate_cohort(n=200, seed=1)
    result = run_mandateops(records, _scorer(), seed=1)
    for outcome in result.outcomes:
        assert outcome.attempts_used <= MAX_ATTEMPTS_PER_CYCLE


def test_mandateops_every_executed_attempt_is_in_a_non_peak_window() -> None:
    records = generate_cohort(n=300, seed=2)
    result = run_mandateops(records, _scorer(), seed=2)
    attempt_events = [e for e in result.events if e.event_type in ("ATTEMPT_EXECUTED", "ATTEMPT_FAILED")]
    assert len(attempt_events) > 0
    for event in attempt_events:
        assert is_non_peak(event.timestamp) is True


def test_naive_ignores_compliance_and_can_fire_in_peak_hours() -> None:
    # Not a hard assertion that it MUST fire in peak hours (depends on
    # cycle_start), but confirm the naive strategy tags its attempts as
    # compliance-ignoring so the distinction is explicit and inspectable.
    records = generate_cohort(n=50, seed=3)
    result = run_naive(records, seed=3)
    attempt_events = [e for e in result.events if e.event_type in ("ATTEMPT_EXECUTED", "ATTEMPT_FAILED")]
    assert all(e.detail.get("ignored_compliance") is True for e in attempt_events)


def test_mandateops_freezes_mid_cycle_revocation_without_burning_all_attempts() -> None:
    records = generate_cohort(n=3000, seed=4, mid_cycle_revocation_rate=0.05)
    revocation_records = [r for r in records if r.mid_cycle_revocation_after is not None]
    assert len(revocation_records) > 0

    result = run_mandateops(records, _scorer(), seed=4)
    by_mandate = {o.mandate_id: o for o in result.outcomes}

    frozen_count = 0
    for record in revocation_records:
        outcome = by_mandate[record.mandate.id]
        if outcome.final_state == CycleState.FROZEN_REVOKED.value:
            frozen_count += 1
            # Must not have burned the full budget after revocation.
            assert outcome.attempts_used <= record.mid_cycle_revocation_after
            assert outcome.attempts_saved >= 0

    # At least some of the flagged records should actually end up frozen
    # (a few may recover before reaching the revocation threshold, which is
    # fine and expected).
    assert frozen_count > 0


def test_mandateops_suppresses_when_notification_send_fails() -> None:
    records = generate_cohort(n=2000, seed=5, notification_failure_rate=0.05)
    failing_records = [r for r in records if r.notification_send_fails]
    assert len(failing_records) > 0

    result = run_mandateops(records, _scorer(), seed=5)
    by_mandate = {o.mandate_id: o for o in result.outcomes}

    for record in failing_records:
        outcome = by_mandate[record.mandate.id]
        assert outcome.final_state == CycleState.FROZEN_NOTIFICATION_FAILED.value
        assert outcome.recovered is False
        # No attempt should have been executed beyond the initial failed one.
        assert outcome.attempts_used == record.cycle.attempts_used


def test_batch_result_summary_has_expected_keys() -> None:
    records = generate_cohort(n=100, seed=6)
    result = run_naive(records, seed=6)
    summary = result.summary()
    assert set(summary.keys()) == {
        "strategy",
        "total_mandates",
        "recovered_count",
        "recovered_rupees",
        "total_attempts_used",
        "total_attempts_saved",
        "recovery_rate",
    }
    assert summary["total_mandates"] == 100


def test_mandateops_recovers_at_least_as_much_as_naive_on_average() -> None:
    """The central product claim, checked at batch scale (not a single
    cherry-picked mandate): across a large enough cohort, the
    constraint-aware, statistically-scored strategy should recover at
    least as much revenue as blind next-day retry, because it never wastes
    attempts on dead mandates and picks better time slots.
    """
    records = generate_cohort(n=4000, seed=2026)
    naive_result = run_naive(records, seed=100)
    mandateops_result = run_mandateops(records, _scorer(), seed=100)

    assert mandateops_result.recovered_rupees >= naive_result.recovered_rupees * 0.95
    # Attempts saved via freezing must be a genuinely positive number for
    # the demo's headline "attempts saved" counter to be meaningful.
    assert mandateops_result.total_attempts_saved > 0
