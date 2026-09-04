"""Unit tests for app.core.rules — the compliance rulebook.

These tests are the specification. If a test here fails, either the rule
implementation is wrong, or a source-cited rule genuinely changed and this
file (plus the README citation) needs a deliberate update — never the
other way around.
"""

from datetime import datetime, timedelta

from app.core.rules import (
    MAX_ATTEMPTS_PER_CYCLE,
    MIN_NOTIFICATION_LEAD_TIME,
    check_attempt_eligibility,
    has_sufficient_notification_lead_time,
    is_non_peak,
    next_non_peak_slot,
)


def test_max_attempts_is_four() -> None:
    assert MAX_ATTEMPTS_PER_CYCLE == 4


def test_notification_lead_time_is_24_hours() -> None:
    assert MIN_NOTIFICATION_LEAD_TIME == timedelta(hours=24)


def test_is_non_peak_early_morning() -> None:
    moment = datetime(2026, 1, 5, 6, 0)  # 06:00 -> inside before-10am window
    assert is_non_peak(moment) is True


def test_is_non_peak_midday_window() -> None:
    moment = datetime(2026, 1, 5, 14, 0)  # 14:00 -> inside 13:00-17:00 window
    assert is_non_peak(moment) is True


def test_is_non_peak_late_night() -> None:
    moment = datetime(2026, 1, 5, 22, 0)  # 22:00 -> inside after-21:30 window
    assert is_non_peak(moment) is True


def test_is_peak_hour_blocked() -> None:
    moment = datetime(2026, 1, 5, 11, 0)  # 11:00 -> peak, blocked
    assert is_non_peak(moment) is False


def test_is_peak_evening_blocked() -> None:
    moment = datetime(2026, 1, 5, 19, 0)  # 19:00 -> peak, blocked
    assert is_non_peak(moment) is False


def test_next_non_peak_slot_from_peak_hour() -> None:
    peak_moment = datetime(2026, 1, 5, 11, 0)
    result = next_non_peak_slot(peak_moment)
    assert is_non_peak(result) is True
    assert result >= peak_moment


def test_next_non_peak_slot_already_non_peak_returns_same() -> None:
    non_peak_moment = datetime(2026, 1, 5, 6, 0)
    result = next_non_peak_slot(non_peak_moment)
    assert result == non_peak_moment


def test_notification_lead_time_insufficient_when_none() -> None:
    attempt_time = datetime(2026, 1, 5, 6, 0)
    assert has_sufficient_notification_lead_time(None, attempt_time) is False


def test_notification_lead_time_insufficient_when_too_recent() -> None:
    attempt_time = datetime(2026, 1, 5, 6, 0)
    notification_sent_at = attempt_time - timedelta(hours=23)
    assert has_sufficient_notification_lead_time(notification_sent_at, attempt_time) is False


def test_notification_lead_time_sufficient_at_exactly_24h() -> None:
    attempt_time = datetime(2026, 1, 5, 6, 0)
    notification_sent_at = attempt_time - timedelta(hours=24)
    assert has_sufficient_notification_lead_time(notification_sent_at, attempt_time) is True


def test_eligibility_fails_on_exhausted_budget() -> None:
    attempt_time = datetime(2026, 1, 5, 6, 0)
    notification_sent_at = attempt_time - timedelta(hours=25)
    result = check_attempt_eligibility(
        attempts_used=4,
        attempt_time=attempt_time,
        notification_sent_at=notification_sent_at,
    )
    assert result.passed is False
    assert result.failing_clause == "ATTEMPT_BUDGET_EXHAUSTED"


def test_eligibility_fails_on_peak_hour() -> None:
    attempt_time = datetime(2026, 1, 5, 11, 0)  # peak
    notification_sent_at = attempt_time - timedelta(hours=25)
    result = check_attempt_eligibility(
        attempts_used=0,
        attempt_time=attempt_time,
        notification_sent_at=notification_sent_at,
    )
    assert result.passed is False
    assert result.failing_clause == "OUTSIDE_NON_PEAK_WINDOW"


def test_eligibility_fails_on_insufficient_notification() -> None:
    attempt_time = datetime(2026, 1, 5, 6, 0)  # non-peak
    notification_sent_at = attempt_time - timedelta(hours=1)
    result = check_attempt_eligibility(
        attempts_used=0,
        attempt_time=attempt_time,
        notification_sent_at=notification_sent_at,
    )
    assert result.passed is False
    assert result.failing_clause == "NOTIFICATION_LEAD_TIME_INSUFFICIENT"


def test_eligibility_passes_when_all_clauses_satisfied() -> None:
    attempt_time = datetime(2026, 1, 5, 6, 0)  # non-peak
    notification_sent_at = attempt_time - timedelta(hours=25)
    result = check_attempt_eligibility(
        attempts_used=1,
        attempt_time=attempt_time,
        notification_sent_at=notification_sent_at,
    )
    assert result.passed is True
    assert result.failing_clause is None
