"""Synthetic historical retry-outcome generator.

This produces the training data the empirical-Bayes scorer (scorer.py)
learns from. It is intentionally separate from the *live demo* cohort
generator (see app/simulation/cohort.py) — historical data represents
"outcomes we've already observed from past cycles," while the live cohort
represents "mandates currently failing, that we're about to schedule retries
for." Conflating the two would let the scorer cheat by training on the exact
batch it's being evaluated against.

Everything here is seeded and deterministic: same seed -> same dataset,
which matters for reproducible demo runs and for the "re-run and get the
same number" trust beat described in BUILD-BLUEPRINT.md.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.core.enums import DeclineCategory
from app.statistical.constants import BANKS, LEGAL_HOURS


@dataclass(frozen=True)
class HistoricalOutcome:
    """One observed (bank, decline category, hour-of-retry) -> success/fail
    data point from a past billing cycle's retry attempt.
    """

    bank_code: str
    decline_category: str  # DeclineCategory value
    hour: int
    success: bool


# Baseline retry-success probability by decline category, before any bank
# or hour adjustment. These are deliberately distinct so the categories
# behave differently in the heatmap — e.g. insufficient-funds genuinely
# does get better later in the day (salary/credit timing), while
# mandate_paused/revoked are structurally almost never worth retrying
# (the deterministic engine should be freezing those anyway; this dataset
# exists mostly to prove the scorer doesn't need to be told that by hand).
BASELINE_SUCCESS_RATE: dict[DeclineCategory, float] = {
    DeclineCategory.INSUFFICIENT_FUNDS: 0.28,
    DeclineCategory.BANK_DOWN: 0.35,
    DeclineCategory.MANDATE_PAUSED: 0.03,
    DeclineCategory.MANDATE_REVOKED: 0.01,
    DeclineCategory.OTHER: 0.20,
}

# Hour-of-day multiplier on top of the baseline, modelling realistic
# behaviour: insufficient-funds retries do better late evening / early
# morning (post-salary-credit windows); bank-down retries do better a few
# hours after a typical outage clears. Only legal (non-peak) hours are ever
# used for scheduling, but we still generate data across all 24h so the
# scorer has genuine signal about *why* certain legal hours outperform others.
HOUR_MULTIPLIER: dict[DeclineCategory, dict[int, float]] = {
    DeclineCategory.INSUFFICIENT_FUNDS: {
        **{h: 0.8 for h in range(24)},
        **{h: 1.6 for h in (0, 1, 2, 3, 4, 5, 6, 22, 23)},  # night/early AM
        **{h: 1.3 for h in (13, 14, 15, 16)},
    },
    DeclineCategory.BANK_DOWN: {
        **{h: 1.0 for h in range(24)},
        **{h: 1.5 for h in (6, 7, 8, 13, 14, 22)},
    },
    DeclineCategory.MANDATE_PAUSED: {h: 1.0 for h in range(24)},
    DeclineCategory.MANDATE_REVOKED: {h: 1.0 for h in range(24)},
    DeclineCategory.OTHER: {h: 1.0 for h in range(24)},
}


def _weighted_bank_choice(rng: random.Random) -> str:
    total = sum(b.volume_weight for b in BANKS)
    r = rng.uniform(0, total)
    upto = 0.0
    for b in BANKS:
        upto += b.volume_weight
        if r <= upto:
            return b.code
    return BANKS[-1].code


def generate_historical_outcomes(
    n: int = 20_000, seed: int = 42
) -> list[HistoricalOutcome]:
    """Generate `n` synthetic historical retry outcomes.

    Deliberately samples hours from the FULL 0-23 range (not just legal
    hours) because real historical data would include attempts made before
    this system existed, or by other systems that didn't respect the
    non-peak constraint — the scorer should still be able to learn from it,
    and the engine (not the scorer) is what enforces legality going forward.
    """
    rng = random.Random(seed)
    from app.statistical.constants import BANKS_BY_CODE

    outcomes: list[HistoricalOutcome] = []
    categories = list(BASELINE_SUCCESS_RATE.keys())

    for _ in range(n):
        bank_code = _weighted_bank_choice(rng)
        bank = BANKS_BY_CODE[bank_code]
        category = rng.choice(categories)
        hour = rng.randint(0, 23)

        base = BASELINE_SUCCESS_RATE[category]
        hour_mult = HOUR_MULTIPLIER[category][hour]
        p = min(0.95, max(0.01, base * hour_mult * bank.reliability_factor))

        success = rng.random() < p
        outcomes.append(
            HistoricalOutcome(
                bank_code=bank_code,
                decline_category=category.value,
                hour=hour,
                success=success,
            )
        )

    return outcomes
