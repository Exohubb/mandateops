"""The simulated "real world" an attempt is executed against.

This is deliberately separate from app.statistical.historical_data even
though it reuses the same baseline/hour-multiplier shape: historical_data
represents what the scorer has LEARNED from past cycles, while this module
represents what ACTUALLY happens when an attempt fires during the live
simulation. Keeping them conceptually distinct (even though calibrated
consistently) is what makes "the statistical layer's predictions actually
pay off" a genuine result rather than a staged one.
"""

from __future__ import annotations

import random

from app.core.enums import DeclineCategory
from app.statistical.constants import BANKS_BY_CODE
from app.statistical.historical_data import BASELINE_SUCCESS_RATE, HOUR_MULTIPLIER


def success_probability(bank_code: str, decline_category: str, hour: int) -> float:
    """The true (simulated) probability that an attempt for this
    (bank, decline_category, hour) combination succeeds. Same functional
    form as historical_data's generator, evaluated at a specific hour.
    """
    category = DeclineCategory(decline_category)
    bank = BANKS_BY_CODE.get(bank_code)
    reliability = bank.reliability_factor if bank else 1.0

    base = BASELINE_SUCCESS_RATE[category]
    hour_mult = HOUR_MULTIPLIER[category][hour]
    return min(0.95, max(0.01, base * hour_mult * reliability))


def draw_outcome(rng: random.Random, bank_code: str, decline_category: str, hour: int) -> bool:
    """Draw a single True/False (success/fail) outcome for one attempt."""
    p = success_probability(bank_code, decline_category, hour)
    return rng.random() < p
