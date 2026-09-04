"""Synthetic cohort generator for the live demo batch.

Produces a set of Mandate + Cycle pairs representing "mandates that just
failed their initial debit attempt and are now entering the recovery
process" — this is the batch the simulation engine (app/simulation/engine.py,
built next) runs forward through simulated time, and the batch the
Naive-vs-MandateOps comparison is computed over.

Deliberately a SEPARATE generator from historical_data.py: this cohort is
"the current problem," historical data is "what the scorer already learned
from the past." A fixed seed keeps demo runs reproducible.
"""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.core.enums import CycleState, DeclineCategory, MandateStatus
from app.core.models import Cycle, Mandate
from app.statistical.constants import BANKS, DECLINE_TEXT_VARIANTS

# Rough real-world-informed mix of *why* a mandate is entering recovery at
# all (i.e. the reason its FIRST attempt failed). Insufficient funds
# dominates in practice; a small tail is already-dead mandates (paused or
# revoked) that a naive system would still try to retry blindly - this is
# precisely the population the revocation-freeze failure-recovery scenario
# is drawn from.
INITIAL_FAILURE_MIX: dict[DeclineCategory, float] = {
    DeclineCategory.INSUFFICIENT_FUNDS: 0.55,
    DeclineCategory.BANK_DOWN: 0.20,
    DeclineCategory.OTHER: 0.12,
    DeclineCategory.MANDATE_PAUSED: 0.07,
    DeclineCategory.MANDATE_REVOKED: 0.06,
}

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Ananya", "Diya", "Ishaan", "Kabir", "Meera",
    "Neha", "Priya", "Rohan", "Sanya", "Tara", "Vihaan", "Zara", "Arjun",
    "Kiara", "Advait", "Riya", "Yash",
]
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Iyer", "Nair", "Reddy", "Patel", "Singh",
    "Rao", "Menon", "Kapoor", "Chatterjee", "Das", "Joshi", "Mehta",
]


@dataclass(frozen=True)
class SyntheticCycleRecord:
    """A generated (Mandate, Cycle, initial decline text) triple, before any
    simulated time has passed. The simulation engine consumes these to seed
    a run.
    """

    mandate: Mandate
    cycle: Cycle
    initial_decline_text: str
    initial_decline_category: str  # DeclineCategory value


def _weighted_bank_choice(rng: random.Random) -> str:
    total = sum(b.volume_weight for b in BANKS)
    r = rng.uniform(0, total)
    upto = 0.0
    for b in BANKS:
        upto += b.volume_weight
        if r <= upto:
            return b.code
    return BANKS[-1].code


def _weighted_category_choice(rng: random.Random) -> DeclineCategory:
    r = rng.random()
    upto = 0.0
    for category, weight in INITIAL_FAILURE_MIX.items():
        upto += weight
        if r <= upto:
            return category
    return DeclineCategory.OTHER


def generate_cohort(
    n: int = 5_000, seed: int = 2026, cycle_start: datetime | None = None
) -> list[SyntheticCycleRecord]:
    """Generate `n` synthetic mandates, each with exactly one billing cycle
    that has already failed its initial attempt and is entering recovery.

    `cycle_start` anchors the simulated clock's "day zero" — defaults to a
    fixed date so demo runs are reproducible unless the caller overrides it.
    """
    rng = random.Random(seed)
    start = cycle_start or datetime(2026, 1, 1, 9, 0)

    records: list[SyntheticCycleRecord] = []
    for i in range(n):
        bank_code = _weighted_bank_choice(rng)
        category = _weighted_category_choice(rng)
        decline_text = rng.choice(DECLINE_TEXT_VARIANTS[category])

        # Mandate rail-status is mostly ACTIVE; a slice matches the
        # decline category so the population is internally consistent
        # (a mandate whose first decline was "mandate_revoked" text is
        # actually REVOKED on the rail, etc.) — this is what makes the
        # revocation-freeze scenario a realistic subset of the batch
        # rather than a hand-picked single example.
        if category == DeclineCategory.MANDATE_REVOKED:
            mandate_status = MandateStatus.REVOKED
        elif category == DeclineCategory.MANDATE_PAUSED:
            mandate_status = MandateStatus.PAUSED
        else:
            mandate_status = MandateStatus.ACTIVE

        name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
        plan_amount_paise = rng.choice([9900, 19900, 29900, 49900, 99900, 149900])

        mandate_id = f"mandate-{i:05d}-{uuid.uuid4().hex[:8]}"
        cycle_id = f"cycle-{i:05d}-{uuid.uuid4().hex[:8]}"

        mandate = Mandate(
            id=mandate_id,
            subscriber_name=name,
            bank=bank_code,
            plan_amount_paise=plan_amount_paise,
            status=mandate_status,
            created_at=start - timedelta(days=rng.randint(30, 400)),
        )

        cycle = Cycle(
            id=cycle_id,
            mandate_id=mandate_id,
            cycle_number=rng.randint(1, 12),
            state=CycleState.PENDING,
            attempts_used=1,  # the initial attempt already happened and failed
            notification_sent_at=None,  # recovery-cycle notice not yet sent
            recovered_amount_paise=0,
            created_at=start,
        )

        records.append(
            SyntheticCycleRecord(
                mandate=mandate,
                cycle=cycle,
                initial_decline_text=decline_text,
                initial_decline_category=category.value,
            )
        )

    return records
