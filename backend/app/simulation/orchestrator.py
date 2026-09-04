"""Batch orchestration: ties the cohort generator, AI classification,
both simulation strategies, and persistence together into one coherent
"run a batch" operation that the API layer calls.

This is intentionally the only module that imports from app.db AND
app.simulation AND app.ai at once — everything else stays layered.
"""

from __future__ import annotations

import uuid

import aiosqlite

from app.ai.gemini_client import classify_declines_batch, executive_summary
from app.core.enums import ActorLayer
from app.db import repository
from app.simulation.cohort import generate_cohort
from app.simulation.ground_truth import success_probability
from app.simulation.runner import run_mandateops, run_naive
from app.statistical.historical_data import generate_historical_outcomes
from app.statistical.scorer import RetrySlotScorer

# Fixed historical training set — generated once per process, shared across
# batch runs, since it represents "what we already know from the past" and
# should not be regenerated per run.
_HISTORICAL_OUTCOMES = generate_historical_outcomes(n=20_000, seed=42)
_SCORER = RetrySlotScorer(_HISTORICAL_OUTCOMES)


def get_scorer() -> RetrySlotScorer:
    return _SCORER


async def run_batch(
    conn: aiosqlite.Connection, *, cohort_size: int = 50, seed: int = 2026
) -> str:
    """Run a full batch: generate cohort, classify decline text via AI
    (batched, with automatic fallback), run both strategies, persist
    everything, and write the audit trail. Returns the new batch_id.
    """
    batch_id = f"batch-{uuid.uuid4().hex[:10]}"
    await repository.create_batch_run(conn, batch_id=batch_id, cohort_size=cohort_size, seed=seed)

    records = generate_cohort(n=cohort_size, seed=seed)

    # --- AI Job 1: batched decline-reason normalization -------------------
    # Decline text comes from a small fixed vocabulary (see
    # app.statistical.constants.DECLINE_TEXT_VARIANTS) — a 5,000-mandate
    # cohort has only ~25 DISTINCT raw strings, repeated thousands of times.
    # Deduplicating before calling Gemini turns this into a single small
    # batch call (well under the 50-per-call chunk size) regardless of
    # cohort size, instead of scaling with the number of mandates. This is
    # the difference between ~1 Gemini call and ~100+ calls for the same
    # batch, and it's what keeps a free-tier daily quota from being burned
    # by a single run.
    unique_texts = sorted(set(r.initial_decline_text for r in records))
    unique_classifications: dict[str, tuple] = {}
    batch_group_size = 50
    for start in range(0, len(unique_texts), batch_group_size):
        chunk = unique_texts[start : start + batch_group_size]
        results = await classify_declines_batch(chunk)
        for text, result in zip(chunk, results, strict=True):
            unique_classifications[text] = result

    classified_by_mandate = {
        r.mandate.id: unique_classifications[r.initial_decline_text][1] for r in records
    }
    decline_texts_by_mandate = {r.mandate.id: r.initial_decline_text for r in records}
    subscriber_names_by_mandate = {r.mandate.id: r.mandate.subscriber_name for r in records}

    # --- Run both strategies -----------------------------------------------
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

    # --- Audit trail: one entry per MandateOps event, hash-chained --------
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

    # --- AI Job 4: executive summary ---------------------------------------
    naive_summary = naive_result.summary()
    mandateops_summary = mandateops_result.summary()
    combined_stats = {
        "total_mandates": cohort_size,
        "naive_recovered_rupees": naive_summary["recovered_rupees"],
        "recovered_rupees": mandateops_summary["recovered_rupees"],
        "naive_recovery_rate": naive_summary["recovery_rate"],
        "mandateops_recovery_rate": mandateops_summary["recovery_rate"],
        "attempts_saved": mandateops_summary["total_attempts_saved"],
    }
    summary_text = await executive_summary(batch_stats=combined_stats)

    await repository.complete_batch_run(
        conn,
        batch_id=batch_id,
        naive_summary=naive_summary,
        mandateops_summary=mandateops_summary,
        executive_summary_text=summary_text,
    )

    return batch_id


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
