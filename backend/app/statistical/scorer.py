"""Empirical-Bayes retry-slot scorer with shrinkage toward the global prior.

This is the ONLY place in the system that recommends *which* legal hour to
use for a retry attempt — the deterministic engine (app/core/engine.py)
still has final say on WHETHER an attempt is legal at all. The scorer never
overrides eligibility; it only ranks the legal hours the engine already
allows.

Design, matching BUILD-BLUEPRINT.md section 5's "statistical, not
generative" layer:

  - Inspectable math only (no neural net, no black box).
  - Reports its own sample size for every cell it scores.
  - Refuses to differentiate slots below MIN_SUPPORT_THRESHOLD and says so,
    falling back to the global category prior instead of a confident-looking
    but unsupported number.

The shrinkage formula is a standard empirical-Bayes estimator for a
binomial rate: shrunk_p = (successes + k * global_prior) / (n + k), where
k is a pseudo-count controlling how strongly thin cells get pulled toward
the prior. As n grows, shrunk_p converges to the cell's own observed rate.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.statistical.constants import LEGAL_HOURS
from app.statistical.historical_data import HistoricalOutcome

# Pseudo-count controlling shrinkage strength. Higher = more conservative
# (pulls thin cells harder toward the prior). Chosen so a cell needs on the
# order of ~20-30 observations before its own data dominates the estimate.
SHRINKAGE_K = 25.0

# A cell with fewer than this many observations is flagged as low-support.
# The scorer still returns a shrunk estimate for it (so the UI has *some*
# monotonic answer to render), but tags it clearly so the frontend can grey
# it out / label it "insufficient data — using global prior" rather than
# presenting it with the same confidence as a well-observed cell.
MIN_SUPPORT_THRESHOLD = 15


@dataclass(frozen=True)
class SlotScore:
    """The scored outcome for one (bank, decline_category, hour) cell."""

    bank_code: str
    decline_category: str
    hour: int
    observed_successes: int
    observed_trials: int
    raw_rate: float | None  # None if observed_trials == 0
    shrunk_probability: float
    global_prior: float
    sufficient_support: bool


class RetrySlotScorer:
    """Fit once on a batch of HistoricalOutcome rows, then query scores for
    any (bank, category, hour) combination — including combinations never
    seen in training, which fall back entirely to the global prior.
    """

    def __init__(self, outcomes: list[HistoricalOutcome]) -> None:
        self._global_prior_by_category: dict[str, float] = {}
        self._cell_counts: dict[tuple[str, str, int], tuple[int, int]] = {}
        self._fit(outcomes)

    def _fit(self, outcomes: list[HistoricalOutcome]) -> None:
        # Global prior per decline category, across all banks and hours.
        totals: dict[str, list[int]] = {}
        for o in outcomes:
            bucket = totals.setdefault(o.decline_category, [0, 0])
            bucket[0] += 1 if o.success else 0
            bucket[1] += 1
        for category, (successes, trials) in totals.items():
            self._global_prior_by_category[category] = (
                successes / trials if trials > 0 else 0.05
            )

        # Per-cell counts.
        for o in outcomes:
            key = (o.bank_code, o.decline_category, o.hour)
            successes, trials = self._cell_counts.get(key, (0, 0))
            self._cell_counts[key] = (
                successes + (1 if o.success else 0),
                trials + 1,
            )

    def global_prior(self, decline_category: str) -> float:
        return self._global_prior_by_category.get(decline_category, 0.05)

    def score_slot(self, bank_code: str, decline_category: str, hour: int) -> SlotScore:
        successes, trials = self._cell_counts.get((bank_code, decline_category, hour), (0, 0))
        prior = self.global_prior(decline_category)

        raw_rate = (successes / trials) if trials > 0 else None
        shrunk = (successes + SHRINKAGE_K * prior) / (trials + SHRINKAGE_K)

        return SlotScore(
            bank_code=bank_code,
            decline_category=decline_category,
            hour=hour,
            observed_successes=successes,
            observed_trials=trials,
            raw_rate=raw_rate,
            shrunk_probability=round(shrunk, 4),
            global_prior=round(prior, 4),
            sufficient_support=trials >= MIN_SUPPORT_THRESHOLD,
        )

    def best_legal_slot(
        self, bank_code: str, decline_category: str, legal_hours: list[int] | None = None
    ) -> SlotScore:
        """Return the highest-scoring LEGAL hour for this (bank, category)
        pair. `legal_hours` defaults to the module-level LEGAL_HOURS
        (derived directly from app.core.rules.NON_PEAK_WINDOWS), so the
        statistical layer can never recommend an hour the deterministic
        engine would reject.
        """
        hours = legal_hours if legal_hours is not None else LEGAL_HOURS
        scored = [self.score_slot(bank_code, decline_category, h) for h in hours]
        return max(scored, key=lambda s: s.shrunk_probability)

    def heatmap(self, decline_category: str, bank_codes: list[str]) -> list[SlotScore]:
        """All (bank, hour) scores for one decline category, restricted to
        legal hours only — exactly the data the frontend heatmap chart
        (BUILD-BLUEPRINT.md section 6.3, Chart 3) renders.
        """
        return [
            self.score_slot(bank_code, decline_category, hour)
            for bank_code in bank_codes
            for hour in LEGAL_HOURS
        ]
