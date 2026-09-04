"""The Gemini AI service layer — Nira's four bounded jobs.

Per BUILD-BLUEPRINT.md section 5, AI here does exactly four things and
nothing else:
  1. classify_declines_batch  — normalize messy bank decline text (batched)
  2. compose_message          — draft a customer-facing notice/recovery text
  3. ask_copilot               — grounded Q&A over the current batch's data
  4. executive_summary         — one paragraph turning batch stats into prose

No function in this file ever returns a rupee amount, a probability, an
attempt count, or a scheduling decision — those are computed exclusively by
app.core and app.statistical. Gemini only ever reads and writes text.

Every call is: rate-limited -> cache-checked -> (on miss) sent to Gemini ->
on ANY failure, falls back to a deterministic substitute and tags the
result accordingly, per app.ai.fallback.
"""

from __future__ import annotations

import asyncio
import json
import logging

from google import genai
from google.genai import types

from app.ai.cache import ai_cache, content_hash
from app.ai.fallback import classify_batch_fallback
from app.ai.persona import NIRA_SYSTEM_INSTRUCTION
from app.ai.rate_limiter import rpm_to_limiter
from app.config import get_settings
from app.core.enums import ClassifiedBy, DeclineCategory

logger = logging.getLogger("mandateops.ai")

# The google-genai SDK's generate_content call is synchronous and, left to
# its own defaults, retries internally on 429s using the server's suggested
# retry-after delay (which can be 30-60+ seconds on a free-tier quota hit).
# Running that directly inside an `async def` blocks the entire event loop
# for the whole retry duration — every other request the backend is
# serving (including /api/health) freezes too. Two fixes, applied to every
# call below: (1) disable the SDK's internal retries (attempts=1) so a
# rate-limit error surfaces immediately and our own fallback takes over
# instantly instead of waiting it out, and (2) run the call in a worker
# thread via asyncio.to_thread so even a slow-but-successful call can't
# block concurrent requests.
_HTTP_OPTIONS = types.HttpOptions(
    timeout=15_000,  # milliseconds
    retry_options=types.HttpRetryOptions(attempts=1),
)

# Free-tier RPM assumptions per model family (see BUILD-BLUEPRINT.md section
# 5.3 and the 2026 quota research) — deliberately conservative so the
# in-process limiter never actually trips a real 429 against the account.
_FAST_MODEL_RPM = 10
_REASONING_MODEL_RPM = 8

_fast_limiter = rpm_to_limiter(_FAST_MODEL_RPM)
_reasoning_limiter = rpm_to_limiter(_REASONING_MODEL_RPM)

_VALID_CATEGORIES = {c.value for c in DeclineCategory if c != DeclineCategory.UNCLASSIFIED}


class GeminiUnavailableError(Exception):
    """Raised internally when Gemini cannot be reached or is not
    configured. Callers in this module catch it and fall back; it should
    never escape to the API layer.
    """


def _get_client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_configured:
        raise GeminiUnavailableError("GEMINI_API_KEY not configured")
    return genai.Client(api_key=settings.gemini_api_key, http_options=_HTTP_OPTIONS)


async def _generate_content(client: genai.Client, **kwargs):
    """Run the SDK's synchronous generate_content call off the event loop,
    so a slow or retrying call never blocks other concurrent requests.
    """
    return await asyncio.to_thread(client.models.generate_content, **kwargs)


# --- Job 1: batched decline-reason normalization --------------------------

_CLASSIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "classifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "category": {
                        "type": "string",
                        "enum": sorted(_VALID_CATEGORIES),
                    },
                    "confident": {"type": "boolean"},
                },
                "required": ["index", "category", "confident"],
            },
        }
    },
    "required": ["classifications"],
}


async def classify_declines_batch(
    raw_texts: list[str],
) -> list[tuple[DeclineCategory, str]]:
    """Classify up to ~50 raw decline strings in a single Gemini call.

    Returns a list parallel to `raw_texts` of (category, classified_by).
    Falls back to the deterministic keyword classifier — per-item — for any
    entry Gemini fails to return or fails on, and for the whole batch if
    Gemini is unavailable at all.
    """
    if not raw_texts:
        return []

    cache_key = content_hash("classify_batch", *raw_texts)
    cached = ai_cache.get(cache_key)
    if cached is not None:
        parsed = json.loads(cached)
        return [(DeclineCategory(c), ClassifiedBy.NIRA.value) for c in parsed]

    try:
        client = _get_client()
        await _fast_limiter.acquire()

        numbered = "\n".join(f"{i}: {text}" for i, text in enumerate(raw_texts))
        prompt = (
            "Classify each of the following bank decline messages into exactly "
            "one category. Each line is formatted as '<index>: <raw text>'.\n\n"
            f"{numbered}\n\n"
            "Return a classification for every index, in the same order."
        )

        settings = get_settings()
        response = await _generate_content(
            client,
            model=settings.gemini_model_fast,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=NIRA_SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=_CLASSIFY_SCHEMA,
                temperature=0.1,
            ),
        )

        parsed = json.loads(response.text)
        by_index: dict[int, str] = {}
        for item in parsed.get("classifications", []):
            idx = item.get("index")
            category = item.get("category")
            confident = item.get("confident", True)
            if idx is None or category not in _VALID_CATEGORIES:
                continue
            by_index[idx] = category if confident else DeclineCategory.OTHER.value

        results: list[tuple[DeclineCategory, str]] = []
        fallback_needed_texts: list[tuple[int, str]] = []
        for i, text in enumerate(raw_texts):
            if i in by_index:
                results.append((DeclineCategory(by_index[i]), ClassifiedBy.NIRA.value))
            else:
                fallback_needed_texts.append((i, text))
                results.append((DeclineCategory.UNCLASSIFIED, ClassifiedBy.NIRA.value))

        # Any index Gemini didn't return gets the deterministic fallback,
        # applied per-item rather than discarding the whole batch's success.
        if fallback_needed_texts:
            fb_results = classify_batch_fallback([t for _, t in fallback_needed_texts])
            for (idx, _), fb in zip(fallback_needed_texts, fb_results, strict=True):
                results[idx] = fb

        cache_payload = json.dumps([r[0].value for r in results])
        ai_cache.set(cache_key, cache_payload)
        return results

    except Exception as exc:  # noqa: BLE001 - any failure -> deterministic fallback
        logger.warning("Gemini classify_declines_batch failed, using fallback: %s", exc)
        return classify_batch_fallback(raw_texts)


# --- Job 2: customer-facing message composer ------------------------------

_APPROVED_TEMPLATE_HINTS = {
    "pre_debit_notice": (
        "a short, polite pre-debit notice telling the customer their "
        "subscription payment of the given amount will be attempted on the "
        "given date, at least 24 hours from now"
    ),
    "recovery_link": (
        "a short, polite message letting the customer know their last "
        "payment did not go through and offering a one-click link to pay "
        "now to keep their subscription active"
    ),
}


async def compose_message(
    *, template: str, amount_rupees: float, language: str = "english"
) -> str:
    """Draft a short customer-facing message for one of the merchant-approved
    template types. `template` must be a key in _APPROVED_TEMPLATE_HINTS —
    Nira drafts wording only, never invents a new message purpose.
    """
    hint = _APPROVED_TEMPLATE_HINTS.get(template)
    if hint is None:
        raise ValueError(f"Unknown approved template: {template}")

    cache_key = content_hash("compose_message", template, str(amount_rupees), language)
    cached = ai_cache.get(cache_key)
    if cached is not None:
        return cached

    fallback_text = (
        f"Your payment of Rs. {amount_rupees:.2f} could not be completed. "
        "Please use the link below to complete your payment and keep your "
        "subscription active."
    )

    try:
        client = _get_client()
        await _fast_limiter.acquire()
        settings = get_settings()

        prompt = (
            f"Draft {hint}. The amount is Rs. {amount_rupees:.2f}. "
            f"Write it in {language}. Keep it under 40 words. Do not include "
            "a placeholder link or say 'click here' — just the message text."
        )
        response = await _generate_content(
            client,
            model=settings.gemini_model_fast,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=NIRA_SYSTEM_INSTRUCTION,
                temperature=0.4,
            ),
        )
        text = (response.text or "").strip() or fallback_text
        ai_cache.set(cache_key, text)
        return text
    except Exception as exc:  # noqa: BLE001
        logger.warning("Gemini compose_message failed, using fallback text: %s", exc)
        return fallback_text


# --- Job 3: grounded AI Copilot chat ---------------------------------------


async def ask_copilot(*, question: str, grounded_context: dict) -> dict:
    """Answer a user's question about the CURRENT batch run only, grounded
    strictly in `grounded_context` (rows/aggregates the caller retrieved
    from SQLite before calling this function — never Gemini's own memory).

    Returns {"answer": str, "grounded": bool, "used_fallback": bool}.
    `grounded` is False if Nira explicitly said she doesn't have the answer
    in the provided data — surfaced by the frontend rather than hidden.
    """
    context_json = json.dumps(grounded_context, default=str, sort_keys=True)
    cache_key = content_hash("ask_copilot", question, context_json)
    cached = ai_cache.get(cache_key)
    if cached is not None:
        return json.loads(cached)

    fallback_answer = {
        "answer": (
            "Nira is temporarily unavailable (AI service unreachable or "
            "rate-limited). The raw data you asked about is still available "
            "in the dashboard tables below."
        ),
        "grounded": False,
        "used_fallback": True,
    }

    try:
        client = _get_client()
        await _reasoning_limiter.acquire()
        settings = get_settings()

        prompt = (
            "Answer the user's question using ONLY the JSON data below, "
            "which describes the current batch run. If the answer is not "
            "contained in this data, say exactly: \"I don't have that in "
            "this run's data.\"\n\n"
            f"DATA:\n{context_json}\n\n"
            f"QUESTION: {question}"
        )
        response = await _generate_content(
            client,
            model=settings.gemini_model_reasoning,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=NIRA_SYSTEM_INSTRUCTION,
                temperature=0.2,
            ),
        )
        text = (response.text or "").strip()
        grounded = "i don't have that in this run's data" not in text.lower()
        result = {"answer": text, "grounded": grounded, "used_fallback": False}
        ai_cache.set(cache_key, json.dumps(result))
        return result
    except Exception as exc:  # noqa: BLE001
        logger.warning("Gemini ask_copilot failed, using fallback: %s", exc)
        return fallback_answer


# --- Job 4: executive summary / recovery certificate narrative -------------


async def executive_summary(*, batch_stats: dict) -> str:
    """Turn a completed batch run's raw numbers into one written paragraph
    for the Recovery Certificate. Called once per completed batch run.
    """
    stats_json = json.dumps(batch_stats, default=str, sort_keys=True)
    cache_key = content_hash("executive_summary", stats_json)
    cached = ai_cache.get(cache_key)
    if cached is not None:
        return cached

    fallback_text = (
        f"This batch processed {batch_stats.get('total_mandates', 'N/A')} mandates. "
        f"MandateOps recovered Rs. {batch_stats.get('recovered_rupees', 'N/A')}, "
        f"compared to Rs. {batch_stats.get('naive_recovered_rupees', 'N/A')} under "
        "naive next-day retry. Full figures are available in the tables above."
    )

    try:
        client = _get_client()
        await _reasoning_limiter.acquire()
        settings = get_settings()

        prompt = (
            "Write one concise paragraph (max 90 words) summarizing this "
            "completed batch run for a finance controller's Recovery "
            "Certificate. Use only the numbers given below — do not invent "
            "any figure. Mention the comparison to naive retry-next-day if "
            "present in the data.\n\n"
            f"DATA:\n{stats_json}"
        )
        response = await _generate_content(
            client,
            model=settings.gemini_model_reasoning,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=NIRA_SYSTEM_INSTRUCTION,
                temperature=0.3,
            ),
        )
        text = (response.text or "").strip() or fallback_text
        ai_cache.set(cache_key, text)
        return text
    except Exception as exc:  # noqa: BLE001
        logger.warning("Gemini executive_summary failed, using fallback: %s", exc)
        return fallback_text
