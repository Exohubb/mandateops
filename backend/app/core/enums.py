"""Domain enums for the deterministic core.

Every value here is a fixed vocabulary the rest of the system (API, UI, audit
log) relies on staying stable. Treat renaming a value as a breaking change.
"""

from enum import StrEnum


class MandateStatus(StrEnum):
    """The rail-side status of a UPI AutoPay mandate itself (not a single cycle)."""

    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class CycleState(StrEnum):
    """The state of one billing cycle's attempt-recovery process."""

    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    RECOVERED = "RECOVERED"
    EXHAUSTED = "EXHAUSTED"
    FROZEN_REVOKED = "FROZEN_REVOKED"
    FROZEN_NOTIFICATION_FAILED = "FROZEN_NOTIFICATION_FAILED"


class AttemptOutcome(StrEnum):
    """The result of one executed (or suppressed) debit attempt."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SUPPRESSED = "SUPPRESSED"


class DeclineCategory(StrEnum):
    """Canonical taxonomy that messy bank decline text gets normalized into.

    This is the ONLY place AI (or its deterministic fallback) is allowed to
    write a category label. Nothing downstream computes this from scratch.
    """

    INSUFFICIENT_FUNDS = "insufficient_funds"
    BANK_DOWN = "bank_down"
    MANDATE_PAUSED = "mandate_paused"
    MANDATE_REVOKED = "mandate_revoked"
    OTHER = "other"
    UNCLASSIFIED = "unclassified"


class ClassifiedBy(StrEnum):
    """Which layer produced a decline classification. Always shown in the UI
    so a judge can see, per record, whether AI or a fallback rule made the call.
    """

    DETERMINISTIC_RULE = "deterministic_rule"
    NIRA = "nira"
    FALLBACK_RULE_ENGINE = "fallback_rule_engine"


class ActorLayer(StrEnum):
    """Which architectural layer produced a given audit-log event.

    This is the tag that makes the "AI judgment" split visible and provable
    on every single row of the audit trail, not just asserted in a README.
    """

    DETERMINISTIC = "deterministic"
    STATISTICAL = "statistical"
    AI = "ai"


class DecisionType(StrEnum):
    """The possible outcomes of evaluating a mandate cycle at a point in time.

    Produced by app.core.engine.evaluate_cycle — the single deterministic
    decision function that decides what happens next for a cycle.
    """

    SCHEDULE_ATTEMPT = "SCHEDULE_ATTEMPT"
    SUPPRESS_NOTIFICATION_MISSING = "SUPPRESS_NOTIFICATION_MISSING"
    FREEZE_REVOKED = "FREEZE_REVOKED"
    FREEZE_PAUSED = "FREEZE_PAUSED"
    EXHAUSTED = "EXHAUSTED"
    ALREADY_RECOVERED = "ALREADY_RECOVERED"
    TERMINAL_NO_ACTION = "TERMINAL_NO_ACTION"
