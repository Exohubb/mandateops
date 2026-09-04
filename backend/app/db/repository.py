"""Repository layer: the only place in the app that writes raw SQL.

Every function here takes an `aiosqlite.Connection` explicitly rather than
reaching for a global, so the repository stays testable against a
temporary in-memory database.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import aiosqlite

from app.core.audit import GENESIS_HASH, build_event
from app.core.models import AuditEvent
from app.simulation.events import SimulationEvent
from app.simulation.runner import BatchResult, MandateOutcome


async def create_batch_run(
    conn: aiosqlite.Connection, *, batch_id: str, cohort_size: int, seed: int
) -> None:
    await conn.execute(
        """
        INSERT INTO batch_runs (id, created_at, cohort_size, seed, status)
        VALUES (?, ?, ?, ?, 'running')
        """,
        (batch_id, datetime.now(timezone.utc).isoformat(), cohort_size, seed),
    )
    await conn.commit()


async def complete_batch_run(
    conn: aiosqlite.Connection,
    *,
    batch_id: str,
    naive_summary: dict,
    mandateops_summary: dict,
    executive_summary_text: str,
) -> None:
    await conn.execute(
        """
        UPDATE batch_runs
        SET status = 'completed',
            naive_summary_json = ?,
            mandateops_summary_json = ?,
            executive_summary_text = ?
        WHERE id = ?
        """,
        (
            json.dumps(naive_summary),
            json.dumps(mandateops_summary),
            executive_summary_text,
            batch_id,
        ),
    )
    await conn.commit()


async def mark_ai_enrichment_status(
    conn: aiosqlite.Connection, *, batch_id: str, status: str
) -> None:
    """status is one of 'pending', 'running', 'completed', 'failed' — the
    frontend polls this so it can show a "Nira is upgrading this batch..."
    indicator without blocking on it, and swap in richer text once ready.
    """
    await conn.execute(
        "UPDATE batch_runs SET ai_enrichment_status = ? WHERE id = ?",
        (status, batch_id),
    )
    await conn.commit()


async def update_executive_summary(
    conn: aiosqlite.Connection, *, batch_id: str, executive_summary_text: str
) -> None:
    await conn.execute(
        "UPDATE batch_runs SET executive_summary_text = ? WHERE id = ?",
        (executive_summary_text, batch_id),
    )
    await conn.commit()


async def update_outcome_classifications(
    conn: aiosqlite.Connection,
    *,
    batch_id: str,
    classified_by: dict[str, str],
    decline_category: dict[str, str],
) -> None:
    """Upgrade the classified_by / decline_category columns for every
    outcome row (both strategies) belonging to `batch_id`, once the
    background AI-enrichment task has real classifications ready. Keyed by
    mandate_id, applied across both the naive and mandateops rows for that
    mandate since they share the same underlying decline text.
    """
    rows = [
        (classified_by[mandate_id], decline_category[mandate_id], batch_id, mandate_id)
        for mandate_id in classified_by
    ]
    await conn.executemany(
        """
        UPDATE mandate_outcomes
        SET classified_by = ?, decline_category = ?
        WHERE batch_id = ? AND mandate_id = ?
        """,
        rows,
    )
    await conn.commit()


async def get_batch_run(conn: aiosqlite.Connection, batch_id: str) -> dict | None:
    cursor = await conn.execute("SELECT * FROM batch_runs WHERE id = ?", (batch_id,))
    row = await cursor.fetchone()
    if row is None:
        return None
    result = dict(row)
    for key in ("naive_summary_json", "mandateops_summary_json"):
        if result.get(key):
            result[key.replace("_json", "")] = json.loads(result[key])
    return result


async def list_batch_runs(conn: aiosqlite.Connection, limit: int = 20) -> list[dict]:
    cursor = await conn.execute(
        "SELECT * FROM batch_runs ORDER BY created_at DESC LIMIT ?", (limit,)
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def delete_batch_run(conn: aiosqlite.Connection, batch_id: str) -> bool:
    """Delete a batch run and every row derived from it (outcomes,
    simulation events, audit events) across all four tables. Returns True
    if a batch with this id existed and was deleted, False otherwise.
    """
    cursor = await conn.execute("SELECT 1 FROM batch_runs WHERE id = ?", (batch_id,))
    exists = await cursor.fetchone()
    if exists is None:
        return False

    await conn.execute("DELETE FROM mandate_outcomes WHERE batch_id = ?", (batch_id,))
    await conn.execute("DELETE FROM simulation_events WHERE batch_id = ?", (batch_id,))
    await conn.execute("DELETE FROM audit_events WHERE batch_id = ?", (batch_id,))
    await conn.execute("DELETE FROM batch_runs WHERE id = ?", (batch_id,))
    await conn.commit()
    return True


async def save_outcomes(
    conn: aiosqlite.Connection,
    *,
    batch_id: str,
    strategy: str,
    outcomes: list[MandateOutcome],
    decline_texts: dict[str, str],
    classified_by: dict[str, str],
    subscriber_names: dict[str, str],
) -> None:
    rows = [
        (
            batch_id,
            strategy,
            o.mandate_id,
            o.cycle_id,
            subscriber_names.get(o.mandate_id, "Unknown"),
            o.bank,
            o.decline_category,
            decline_texts.get(o.mandate_id, ""),
            o.final_state,
            o.attempts_used,
            o.attempts_saved,
            1 if o.recovered else 0,
            o.recovered_amount_paise,
            o.plan_amount_paise,
            classified_by.get(o.mandate_id, "deterministic_rule"),
        )
        for o in outcomes
    ]
    await conn.executemany(
        """
        INSERT OR REPLACE INTO mandate_outcomes (
            batch_id, strategy, mandate_id, cycle_id, subscriber_name, bank,
            decline_category, decline_raw_text, final_state, attempts_used,
            attempts_saved, recovered, recovered_amount_paise,
            plan_amount_paise, classified_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    await conn.commit()


async def get_outcomes(
    conn: aiosqlite.Connection, *, batch_id: str, strategy: str, limit: int = 500, offset: int = 0
) -> list[dict]:
    cursor = await conn.execute(
        """
        SELECT * FROM mandate_outcomes
        WHERE batch_id = ? AND strategy = ?
        ORDER BY mandate_id
        LIMIT ? OFFSET ?
        """,
        (batch_id, strategy, limit, offset),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def get_outcome_by_mandate(
    conn: aiosqlite.Connection, *, batch_id: str, strategy: str, mandate_id: str
) -> dict | None:
    cursor = await conn.execute(
        """
        SELECT * FROM mandate_outcomes
        WHERE batch_id = ? AND strategy = ? AND mandate_id = ?
        """,
        (batch_id, strategy, mandate_id),
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


async def save_simulation_events(
    conn: aiosqlite.Connection, *, batch_id: str, strategy: str, events: list[SimulationEvent]
) -> None:
    rows = [
        (
            batch_id,
            strategy,
            i,
            e.timestamp.isoformat(),
            e.mandate_id,
            e.cycle_id,
            e.event_type,
            e.actor_layer,
            json.dumps(e.detail, default=str),
        )
        for i, e in enumerate(events)
    ]
    await conn.executemany(
        """
        INSERT INTO simulation_events (
            batch_id, strategy, sequence, timestamp, mandate_id, cycle_id,
            event_type, actor_layer, detail_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    await conn.commit()


async def get_simulation_events(
    conn: aiosqlite.Connection,
    *,
    batch_id: str,
    strategy: str | None = None,
    mandate_id: str | None = None,
    limit: int = 200,
) -> list[dict]:
    query = "SELECT * FROM simulation_events WHERE batch_id = ?"
    params: list = [batch_id]
    if strategy:
        query += " AND strategy = ?"
        params.append(strategy)
    if mandate_id:
        query += " AND mandate_id = ?"
        params.append(mandate_id)
    query += " ORDER BY sequence LIMIT ?"
    params.append(limit)

    cursor = await conn.execute(query, params)
    rows = await cursor.fetchall()
    results = []
    for r in rows:
        row = dict(r)
        row["detail"] = json.loads(row.pop("detail_json"))
        results.append(row)
    return results


# --- Audit log --------------------------------------------------------------


async def _get_last_hash(conn: aiosqlite.Connection, batch_id: str) -> tuple[str, int]:
    cursor = await conn.execute(
        """
        SELECT this_hash, sequence FROM audit_events
        WHERE batch_id = ? ORDER BY sequence DESC LIMIT 1
        """,
        (batch_id,),
    )
    row = await cursor.fetchone()
    if row is None:
        return GENESIS_HASH, -1
    return row["this_hash"], row["sequence"]


async def append_audit_events(
    conn: aiosqlite.Connection,
    *,
    batch_id: str,
    entries: list[dict],
) -> list[AuditEvent]:
    """Append a batch of audit entries to `batch_id`'s chain, in order.

    Each entry dict needs: actor_layer, event_type, mandate_id, cycle_id,
    detail. Hashes are computed sequentially so the chain stays valid even
    though the whole batch is written in one call.
    """
    prev_hash, last_sequence = await _get_last_hash(conn, batch_id)
    built_events: list[AuditEvent] = []
    sequence = last_sequence

    for i, entry in enumerate(entries):
        sequence += 1
        event = build_event(
            event_id=f"{batch_id}-evt-{sequence}",
            sequence=sequence,
            actor_layer=entry["actor_layer"],
            event_type=entry["event_type"],
            mandate_id=entry.get("mandate_id"),
            cycle_id=entry.get("cycle_id"),
            detail=entry.get("detail", {}),
            prev_hash=prev_hash,
        )
        built_events.append(event)
        prev_hash = event.this_hash

    rows = [
        (
            e.id,
            batch_id,
            e.sequence,
            e.timestamp.isoformat(),
            e.actor_layer,
            e.event_type,
            e.mandate_id,
            e.cycle_id,
            json.dumps(e.detail, default=str),
            e.prev_hash,
            e.this_hash,
        )
        for e in built_events
    ]
    await conn.executemany(
        """
        INSERT INTO audit_events (
            id, batch_id, sequence, timestamp, actor_layer, event_type,
            mandate_id, cycle_id, detail_json, prev_hash, this_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    await conn.commit()
    return built_events


async def get_audit_events(conn: aiosqlite.Connection, batch_id: str) -> list[AuditEvent]:
    cursor = await conn.execute(
        "SELECT * FROM audit_events WHERE batch_id = ? ORDER BY sequence", (batch_id,)
    )
    rows = await cursor.fetchall()
    events = []
    for row in rows:
        events.append(
            AuditEvent(
                id=row["id"],
                sequence=row["sequence"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                actor_layer=row["actor_layer"],
                event_type=row["event_type"],
                mandate_id=row["mandate_id"],
                cycle_id=row["cycle_id"],
                detail=json.loads(row["detail_json"]),
                prev_hash=row["prev_hash"],
                this_hash=row["this_hash"],
            )
        )
    return events
