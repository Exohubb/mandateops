"""Unit tests for app.statistical.scorer — the empirical-Bayes retry-slot
scorer. Verifies shrinkage behaves correctly at the extremes (zero data ->
pure prior; lots of data -> converges to observed rate) and that the scorer
never recommends an illegal hour.
"""

from app.core.enums import DeclineCategory
from app.core.rules import is_non_peak
from app.statistical.historical_data import HistoricalOutcome, generate_historical_outcomes
from app.statistical.scorer import MIN_SUPPORT_THRESHOLD, RetrySlotScorer


def test_reproducible_with_same_seed() -> None:
    a = generate_historical_outcomes(n=500, seed=7)
    b = generate_historical_outcomes(n=500, seed=7)
    assert a == b


def test_different_seed_produces_different_data() -> None:
    a = generate_historical_outcomes(n=500, seed=1)
    b = generate_historical_outcomes(n=500, seed=2)
    assert a != b


def test_unseen_cell_falls_back_entirely_to_global_prior() -> None:
    outcomes = [
        HistoricalOutcome(bank_code="HDFC", decline_category="insufficient_funds", hour=6, success=True)
        for _ in range(100)
    ]
    scorer = RetrySlotScorer(outcomes)
    # A bank/category/hour combination with zero observations.
    score = scorer.score_slot("SIB", "insufficient_funds", 3)
    assert score.observed_trials == 0
    assert score.raw_rate is None
    assert score.sufficient_support is False
    # With zero trials, shrunk probability must equal the global prior exactly.
    assert score.shrunk_probability == round(scorer.global_prior("insufficient_funds"), 4)


def test_well_observed_cell_converges_toward_its_own_rate() -> None:
    # 1000 trials, 900 successes -> raw rate 0.9, far from a plausible prior.
    outcomes = [
        HistoricalOutcome(bank_code="HDFC", decline_category="bank_down", hour=8, success=i < 900)
        for i in range(1000)
    ]
    scorer = RetrySlotScorer(outcomes)
    score = scorer.score_slot("HDFC", "bank_down", 8)
    assert score.observed_trials == 1000
    assert score.sufficient_support is True
    # With 1000 trials and shrinkage k=25, the shrunk estimate should be
    # very close to the raw 0.9 rate (within a small tolerance).
    assert abs(score.shrunk_probability - 0.9) < 0.02


def test_thin_cell_is_flagged_insufficient_support() -> None:
    outcomes = [
        HistoricalOutcome(bank_code="SIB", decline_category="other", hour=6, success=True)
        for _ in range(3)
    ]
    scorer = RetrySlotScorer(outcomes)
    score = scorer.score_slot("SIB", "other", 6)
    assert score.observed_trials == 3
    assert score.observed_trials < MIN_SUPPORT_THRESHOLD
    assert score.sufficient_support is False


def test_best_legal_slot_never_returns_an_illegal_hour() -> None:
    outcomes = generate_historical_outcomes(n=5000, seed=99)
    scorer = RetrySlotScorer(outcomes)
    best = scorer.best_legal_slot("HDFC", DeclineCategory.INSUFFICIENT_FUNDS.value)
    from datetime import datetime

    probe = datetime(2026, 1, 1, best.hour, 30)
    assert is_non_peak(probe) is True


def test_heatmap_covers_all_legal_hours_for_each_bank() -> None:
    from app.statistical.constants import LEGAL_HOURS

    outcomes = generate_historical_outcomes(n=2000, seed=3)
    scorer = RetrySlotScorer(outcomes)
    result = scorer.heatmap("insufficient_funds", ["HDFC", "SBI"])
    assert len(result) == 2 * len(LEGAL_HOURS)
    for score in result:
        assert score.hour in LEGAL_HOURS
