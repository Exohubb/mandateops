"""Shared constants for synthetic data generation and the statistical scorer.

Kept in one place so the historical-outcome generator, the live cohort
generator, and the scorer all agree on the same bank list, decline-text
vocabulary, and legal (non-peak) hour buckets.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.core.enums import DeclineCategory
from app.core.rules import is_non_peak


@dataclass(frozen=True)
class BankProfile:
    """A synthetic bank with a volume weight (how often it appears in the
    cohort — deliberately uneven, so some banks end up with thin historical
    data) and a reliability factor (multiplies retry-success probability for
    the categories where bank quality plausibly matters).
    """

    code: str
    name: str
    volume_weight: float
    reliability_factor: float


# Deliberately uneven volume weights: the big three dominate, and
# "South Indian Bank" is included specifically to guarantee some
# (bank, hour, category) cells stay thin — which is what the scorer's
# minimum-support refusal is supposed to catch and demonstrate honestly.
BANKS: list[BankProfile] = [
    BankProfile("SBI", "State Bank of India", volume_weight=5.0, reliability_factor=0.90),
    BankProfile("HDFC", "HDFC Bank", volume_weight=5.0, reliability_factor=1.10),
    BankProfile("ICICI", "ICICI Bank", volume_weight=5.0, reliability_factor=1.08),
    BankProfile("AXIS", "Axis Bank", volume_weight=3.0, reliability_factor=1.05),
    BankProfile("KOTAK", "Kotak Mahindra Bank", volume_weight=2.0, reliability_factor=1.05),
    BankProfile("PNB", "Punjab National Bank", volume_weight=3.0, reliability_factor=0.85),
    BankProfile("BOB", "Bank of Baroda", volume_weight=3.0, reliability_factor=0.88),
    BankProfile("YES", "Yes Bank", volume_weight=1.5, reliability_factor=0.95),
    BankProfile("IDFC", "IDFC First Bank", volume_weight=1.0, reliability_factor=1.00),
    BankProfile("CANARA", "Canara Bank", volume_weight=2.0, reliability_factor=0.87),
    # Deliberately low volume -> thin cells for the min-support demo.
    BankProfile("SIB", "South Indian Bank", volume_weight=0.3, reliability_factor=0.90),
]

BANKS_BY_CODE: dict[str, BankProfile] = {b.code: b for b in BANKS}


# Messy, realistic raw decline text a bank might actually return, grouped by
# the canonical category it should be normalized into. This is the exact
# vocabulary the AI (Nira) decline-reason normalizer is trained/prompted to
# classify — see app/ai/. The variety and inconsistency here (capitalization,
# abbreviations, phrasing) is deliberate: clean, structured text wouldn't
# need an AI step at all.
DECLINE_TEXT_VARIANTS: dict[DeclineCategory, list[str]] = {
    DeclineCategory.INSUFFICIENT_FUNDS: [
        "Insufficient balance in account",
        "INSUFFICIENT FUNDS",
        "txn declined - insufficient bal",
        "Account has low balance",
        "Decline code 51: Not sufficient funds",
        "insufficient funds in customer account",
    ],
    DeclineCategory.BANK_DOWN: [
        "NPCI issued decline - system unavailable",
        "Issuer bank not responding",
        "Bank server timeout",
        "Unable to process - bank down",
        "Issuer switch inoperative",
        "gateway timeout from issuing bank",
    ],
    DeclineCategory.MANDATE_PAUSED: [
        "Mandate is currently paused by customer",
        "e-mandate paused",
        "AutoPay paused by user",
        "mandate execution paused - customer request",
    ],
    DeclineCategory.MANDATE_REVOKED: [
        "Mandate revoked by customer",
        "e-mandate cancelled by payer",
        "AutoPay disabled by user",
        "mandate no longer active - revoked",
    ],
    DeclineCategory.OTHER: [
        "Unknown error code 5003",
        "Transaction declined by issuer",
        "Generic decline - reason not specified",
        "Do not honour",
        "txn declined - contact bank",
    ],
}


# --- Legal (non-peak) hour buckets ----------------------------------------
# A whole hour h is treated as "legal" for retry scheduling if its midpoint
# (h:30) falls inside a non-peak window per app.core.rules. This gives a
# clean, small set of hourly buckets for the scorer and the UI heatmap,
# consistent with the exact compliance gate the deterministic engine uses.


def _hour_is_legal(hour: int) -> bool:
    probe = datetime(2000, 1, 1, hour, 30)
    return is_non_peak(probe)


LEGAL_HOURS: list[int] = [h for h in range(24) if _hour_is_legal(h)]
