"""Batch orchestration: ties the cohort generator, AI classification,
both simulation strategies, and persistence together into one coherent
"run a batch" operation that the API layer calls.

This is intentionally the only module that imports from app.db AND
app.simulation AND app.ai at once — everything else stays layered.

Speed design: the deterministic + statistical simulation math for a batch
(cohort generation, both strategies, persistence, audit trail) is fast —
milliseconds even for thousands of mandates. The SLOW part is the two AI
calls (decline classification, executive summary), which can take anywhere
from 2 to 45 seconds on the free-tier model this project uses. Making the
user wait on the network round-trip before they can see ANY result is the
actual "Live Simulation is slow" bug — the simulation itself was never
slow.

The fix: `run_batch` now returns as soon as the simulation math is done,
using the deterministic fallback classifier and a deterministic summary
sentence immediately (zero network calls on the request path). A
background task then calls the real AI classification + executive summary
and updates the batch/outcomes in place once ready — the frontend polls
`ai_enrichment_status` and swaps in the richer text/labels when it flips to
'completed', with no need to block the initial response on it.
"""

from __future__ import annotations

import asyncio
import logging
import uuid

import aiosqlite

from app.ai.fallback import classify_batch_fallback
from app.ai.gemini_client import (
    build_fallback_executive_summary,
    classify_declines_batch,
    executive_summary,
)
from app.db import repository
from app.db.connection import get_db
from app.simulation.cohort import generate_cohort
from app.simulation.runner import run_mandateops, run_naive
from app.statistical.historical_data import generate_historical_outcomes
from app.statistical.scorer import RetrySlotScorer

logger = logging.getLogger("mandateops.orchestrator")

# Fixed historical training set — generated once per process, shared across
# batch runs, since it represents "what we already know from the past" and
# should not be regenerated per run.
_HISTORICAL_OUTCOMES = generate_historical_outcomes(n=20_000, seed=42)
_SCORER = RetrySlotScorer(_HISTORICAL_OUTCOMES)


def get_scorer() -> RetrySlotScorer:
    return _SCORER


def _combined_stats(cohort_size: int, naive_summary: dict, mandateops_summary: dict) -> dict:
    return {
        "total_mandates": cohort_size,
        "naive_recovered_rupees": naive_summary["recovered_rupees"],
        "recovered_rupees": mandateops_summary["recovered_rupees"],
        "naive_recovery_rate": naive_summary["recovery_rate"],
        "mandateops_recovery_rate": mandateops_summary["recovery_rate"],
        "attempts_saved": mandateops_summary["total_attempts_saved"],
    }


async def run_batch(
    conn: aiosqlite.Connection, *, cohort_size: int = 50, seed: int = 2026
) -> str:
    """Run a full batch's SIMULATION synchronously (fast, no network calls)
    and return as soon as it's persisted. Decline text is classified with
    the deterministic fallback rules immediately, so the response is never
    blocked on Gemini. A background task (see `_enrich_batch_with_ai`) then
    upgrades the classification and executive summary using the real AI
    once it's ready, without the caller having waited for it.
    """
    batch_id = f"batch-{uuid.uuid4().hex[:10]}"
    await repository.create_batch_run(conn, batch_id=batch_id, cohort_size=cohort_size, seed=seed)

    records = generate_cohort(n=cohort_size, seed=seed)

    # Instant, zero-network classification for the fast path. Every record
    # is honestly tagged classified_by=fallback_rule_engine at this point —
    # the background task below is what upgrades it to Nira.
    unique_texts = sorted(set(r.initial_decline_text for r in records))
    fallback_results = classify_batch_fallback(unique_texts)
    classifications_by_text = dict(zip(unique_texts, fallback_results, strict=True))
    classified_by_mandate = {
        r.mandate.id: classifications_by_text[r.initial_decline_text][1] for r in records
    }
    decline_texts_by_mandate = {r.mandate.id: r.initial_decline_text for r in records}
    subscriber_names_by_mandate = {r.mandate.id: r.mandate.subscriber_name for r in records}

    naive_result = run_naive(records, seed=seed + 1)
    mandateops_result = run_mandateops(records, _SCORER, seed=seed + 1)

    await repository.save_outcomes(
        conn,
        batch_id=batch_id,
        strategy="naive",
        outcomes=naive_result.outcomes,
        decline_texts=decline_texts_by_mandate,
        classified_by=classified_by_mandate,
        subscriber_names=subscriber_names_by_mandate,
    )
    await repository.save_outcomes(
        conn,
        batch_id=batch_id,
        strategy="mandateops",
        outcomes=mandateops_result.outcomes,
        decline_texts=decline_texts_by_mandate,
        classified_by=classified_by_mandate,
        subscriber_names=subscriber_names_by_mandate,
    )

    await repository.save_simulation_events(
        conn, batch_id=batch_id, strategy="naive", events=naive_result.events
    )
    await repository.save_simulation_events(
        conn, batch_id=batch_id, strategy="mandateops", events=mandateops_result.events
    )

    audit_entries = [
        {
            "actor_layer": e.actor_layer,
            "event_type": e.event_type,
            "mandate_id": e.mandate_id,
            "cycle_id": e.cycle_id,
            "detail": e.detail,
        }
        for e in mandateops_result.events
    ]
    await repository.append_audit_events(conn, batch_id=batch_id, entries=audit_entries)

    naive_summary = naive_result.summary()
    mandateops_summary = mandateops_result.summary()
    combined_stats = _combined_stats(cohort_size, naive_summary, mandateops_summary)
    fallback_summary_text = build_fallback_executive_summary(combined_stats)

    await repository.complete_batch_run(
        conn,
        batch_id=batch_id,
        naive_summary=naive_summary,
        mandateops_summary=mandateops_summary,
        executive_summary_text=fallback_summary_text,
    )

    # Fire the slow AI enrichment in the background. Uses its own DB
    # connection handle fetched fresh inside the task rather than closing
    # over `conn`, since the request that triggered this may finish (and
    # its connection borrowing pattern end) well before the task does.
    asyncio.create_task(
        _enrich_batch_with_ai(
            batch_id=batch_id,
            unique_texts=unique_texts,
            records=records,
            naive_summary=naive_summary,
            mandateops_summary=mandateops_summary,
            combined_stats=combined_stats,
        )
    )

    return batch_id


async def _enrich_batch_with_ai(
    *,
    batch_id: str,
    unique_texts: list[str],
    records,
    naive_summary: dict,
    mandateops_summary: dict,
    combined_stats: dict,
) -> None:
    """Background task: call the real AI classifier + executive summary,
    then update the already-saved rows in place. Runs after `run_batch` has
    already returned a full, usable result to the caller — this only
    upgrades quality, it never blocks the initial response.
    """
    conn = get_db()
    try:
        await repository.mark_ai_enrichment_status(conn, batch_id=batch_id, status="running")

        classifications_by_text: dict[str, tuple] = {}
        batch_group_size = 50
        for start in range(0, len(unique_texts), batch_group_size):
            chunk = unique_texts[start : start + batch_group_size]
            results = await classify_declines_batch(chunk)
            for text, result in zip(chunk, results, strict=True):
                classifications_by_text[text] = result

        classified_by_mandate = {
            r.mandate.id: classifications_by_text[r.initial_decline_text][1] for r in records
        }
        decline_categories_by_mandate = {
            r.mandate.id: classifications_by_text[r.initial_decline_text][0].value
            for r in records
        }

        await repository.update_outcome_classifications(
            conn,
            batch_id=batch_id,
            classified_by=classified_by_mandate,
            decline_category=decline_categories_by_mandate,
        )

        summary_text = await executive_summary(batch_stats=combined_stats)
        await repository.update_executive_summary(
            conn, batch_id=batch_id, executive_summary_text=summary_text
        )

        await repository.mark_ai_enrichment_status(conn, batch_id=batch_id, status="completed")
    except Exception:  # noqa: BLE001 - background task must never crash silently unlogged
        logger.exception("AI enrichment failed for batch %s", batch_id)
        await repository.mark_ai_enrichment_status(conn, batch_id=batch_id, status="failed")


def heatmap_data(decline_category: str) -> list[dict]:
    """Retry-slot heatmap data for the frontend's Chart 3 (bank x hour),
    computed directly from the shared scorer instance.
    """
    from app.statistical.constants import BANKS

    bank_codes = [b.code for b in BANKS]
    scores = _SCORER.heatmap(decline_category, bank_codes)
    return [
        {
            "bank_code": s.bank_code,
            "hour": s.hour,
            "shrunk_probability": s.shrunk_probability,
            "observed_trials": s.observed_trials,
            "sufficient_support": s.sufficient_support,
        }
        for s in scores
    ]
