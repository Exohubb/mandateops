"""Unit tests for app.simulation.cohort — the live demo batch generator."""

from app.core.enums import CycleState, DeclineCategory, MandateStatus
from app.simulation.cohort import generate_cohort


def test_generates_requested_count() -> None:
    records = generate_cohort(n=500, seed=1)
    assert len(records) == 500


def test_reproducible_with_same_seed() -> None:
    a = generate_cohort(n=200, seed=42)
    b = generate_cohort(n=200, seed=42)
    assert [r.mandate.subscriber_name for r in a] == [r.mandate.subscriber_name for r in b]
    assert [r.initial_decline_category for r in a] == [r.initial_decline_category for r in b]


def test_all_cycles_start_with_one_attempt_used_and_pending_state() -> None:
    records = generate_cohort(n=300, seed=5)
    for r in records:
        assert r.cycle.attempts_used == 1
        assert r.cycle.state == CycleState.PENDING
        assert r.cycle.notification_sent_at is None


def test_revoked_category_implies_revoked_mandate_status() -> None:
    records = generate_cohort(n=2000, seed=9)
    revoked = [r for r in records if r.initial_decline_category == DeclineCategory.MANDATE_REVOKED.value]
    assert len(revoked) > 0
    assert all(r.mandate.status == MandateStatus.REVOKED for r in revoked)


def test_paused_category_implies_paused_mandate_status() -> None:
    records = generate_cohort(n=2000, seed=9)
    paused = [r for r in records if r.initial_decline_category == DeclineCategory.MANDATE_PAUSED.value]
    assert len(paused) > 0
    assert all(r.mandate.status == MandateStatus.PAUSED for r in paused)


def test_active_category_mix_dominates_population() -> None:
    records = generate_cohort(n=2000, seed=9)
    active = [r for r in records if r.mandate.status == MandateStatus.ACTIVE]
    # insufficient_funds + bank_down + other ~= 87% of INITIAL_FAILURE_MIX
    assert len(active) / len(records) > 0.75


def test_mandate_ids_are_unique() -> None:
    records = generate_cohort(n=1000, seed=11)
    ids = [r.mandate.id for r in records]
    assert len(ids) == len(set(ids))
