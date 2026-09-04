"""Tests for the AI layer's fallback behavior.

Critically, these tests run WITHOUT a configured Gemini API key (the default
test environment has none), which exercises exactly the failure-recovery
path described in BUILD-BLUEPRINT.md section 5.3: every AI job must degrade
to a deterministic substitute rather than raising, and must tag its output
so the degradation is visible rather than silent.
"""

import asyncio

import pytest

from app.ai.fallback import classify_batch_fallback, classify_decline_text_fallback
from app.ai.gemini_client import (
    ask_copilot,
    classify_declines_batch,
    compose_message,
    executive_summary,
)
from app.config import Settings
from app.core.enums import ClassifiedBy, DeclineCategory


@pytest.fixture(autouse=True)
def _force_no_gemini_key(monkeypatch):
    """These tests specifically exercise the fallback path, which must be
    exercised regardless of whether a real GEMINI_API_KEY is present in the
    developer's local .env (it may well be, for actually running the app).
    Forcing get_settings() to report no key here keeps this test file's
    intent correct and fast in both cases.
    """

    def _no_key_settings() -> Settings:
        return Settings(gemini_api_key="")

    monkeypatch.setattr("app.ai.gemini_client.get_settings", _no_key_settings)


def test_fallback_classifies_insufficient_funds() -> None:
    category, classified_by = classify_decline_text_fallback("Insufficient balance in account")
    assert category == DeclineCategory.INSUFFICIENT_FUNDS
    assert classified_by == ClassifiedBy.FALLBACK_RULE_ENGINE.value


def test_fallback_classifies_bank_down() -> None:
    category, _ = classify_decline_text_fallback("Issuer bank not responding")
    assert category == DeclineCategory.BANK_DOWN


def test_fallback_classifies_revoked_before_paused_when_both_keywords_present() -> None:
    # "revoked" rule is checked before "paused" -- ensures explicit priority.
    category, _ = classify_decline_text_fallback("mandate revoked, was previously paused")
    assert category == DeclineCategory.MANDATE_REVOKED


def test_fallback_classifies_unknown_text_as_other() -> None:
    category, _ = classify_decline_text_fallback("some totally novel gibberish decline xyz")
    assert category == DeclineCategory.OTHER


def test_fallback_batch_preserves_order_and_count() -> None:
    texts = [
        "Insufficient balance in account",
        "Issuer bank not responding",
        "mandate revoked by customer",
    ]
    results = classify_batch_fallback(texts)
    assert len(results) == 3
    assert results[0][0] == DeclineCategory.INSUFFICIENT_FUNDS
    assert results[1][0] == DeclineCategory.BANK_DOWN
    assert results[2][0] == DeclineCategory.MANDATE_REVOKED


def test_classify_declines_batch_degrades_without_api_key() -> None:
    """With no GEMINI_API_KEY configured, the async batch classifier must
    still return a full, correctly-shaped result via the fallback path,
    never raise, and never hang.
    """
    texts = ["Insufficient balance in account", "Issuer bank not responding"]
    results = asyncio.run(classify_declines_batch(texts))
    assert len(results) == 2
    for category, classified_by in results:
        assert isinstance(category, DeclineCategory)
        assert classified_by == ClassifiedBy.FALLBACK_RULE_ENGINE.value


def test_compose_message_degrades_without_api_key() -> None:
    text = asyncio.run(
        compose_message(template="recovery_link", amount_rupees=499.0, language="english")
    )
    assert "499.00" in text
    assert len(text) > 0


def test_compose_message_rejects_unknown_template() -> None:
    try:
        asyncio.run(compose_message(template="not_a_real_template", amount_rupees=1.0))
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_ask_copilot_degrades_without_api_key() -> None:
    result = asyncio.run(
        ask_copilot(question="How many mandates recovered?", grounded_context={"recovered": 42})
    )
    assert result["used_fallback"] is True
    assert result["grounded"] is False
    assert len(result["answer"]) > 0


def test_executive_summary_degrades_without_api_key() -> None:
    stats = {
        "total_mandates": 5000,
        "recovered_rupees": 120000,
        "naive_recovered_rupees": 90000,
    }
    text = asyncio.run(executive_summary(batch_stats=stats))
    assert "5000" in text
    assert "120000" in text
