"""Deterministic fallback decline-text classifier.

Used automatically whenever the Gemini call for Job #1 (decline-reason
normalization) fails, is rate-limited, or Gemini is simply not configured
(no API key). This is not a lesser feature bolted on as an afterthought —
per BUILD-BLUEPRINT.md section 5.3, this fallback IS the failure-recovery
demo beat for the AI layer: pull the key, throttle it, or otherwise make
Gemini unavailable, and the system keeps working, tagging every record it
touches `classified_by: fallback_rule_engine` instead of `classified_by:
nira` so the degradation is honest and visible rather than hidden.

Pure keyword matching, zero network calls, zero randomness.
"""

from __future__ import annotations

from app.core.enums import ClassifiedBy, DeclineCategory

# Ordered list of (keywords, category) — checked top to bottom, first match
# wins. Order matters: more specific phrases before more generic ones.
_KEYWORD_RULES: list[tuple[list[str], DeclineCategory]] = [
    (["revoked", "cancelled by payer", "disabled by user", "no longer active"], DeclineCategory.MANDATE_REVOKED),
    (["paused", "pause"], DeclineCategory.MANDATE_PAUSED),
    (["insufficient", "not sufficient funds", "low balance", "51:"], DeclineCategory.INSUFFICIENT_FUNDS),
    (["not responding", "timeout", "system unavailable", "bank down", "inoperative", "gateway timeout"], DeclineCategory.BANK_DOWN),
]


def classify_decline_text_fallback(raw_text: str) -> tuple[DeclineCategory, str]:
    """Classify one raw decline string using simple keyword matching.

    Returns (category, classified_by) where classified_by is always
    ClassifiedBy.FALLBACK_RULE_ENGINE — the caller is responsible for
    persisting/displaying that tag alongside the category.
    """
    lowered = raw_text.lower()
    for keywords, category in _KEYWORD_RULES:
        if any(kw in lowered for kw in keywords):
            return category, ClassifiedBy.FALLBACK_RULE_ENGINE.value
    return DeclineCategory.OTHER, ClassifiedBy.FALLBACK_RULE_ENGINE.value


def classify_batch_fallback(raw_texts: list[str]) -> list[tuple[DeclineCategory, str]]:
    """Batch convenience wrapper — same interface shape as the Gemini batch
    classifier in gemini_client.py, so callers can swap between the two
    without changing call sites.
    """
    return [classify_decline_text_fallback(t) for t in raw_texts]
