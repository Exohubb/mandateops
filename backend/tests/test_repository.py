"""Integration tests for app.db.repository against a real (temporary)
SQLite file — verifying persistence round-trips and audit-chain integrity
survive an actual write/read cycle, not just in-memory dataclasses.
"""

from app.core.audit import verify_chain
from app.db import repository
from app.simulation.cohort import generate_cohort
from app.simulation.orchestrator import get_scorer
from app.simulation.runner import run_mandateops, run_naive


async def test_create_and_get_batch_run(test_db):
    await repository.create_batch_run(test_db, batch_id="b1", cohort_size=100, seed=1)
    batch = await repository.get_batch_run(test_db, "b1")
    assert batch is not None
    assert batch["status"] == "running"
    assert batch["cohort_size"] == 100


async def test_complete_batch_run_stores_summaries(test_db):
    await repository.create_batch_run(test_db, batch_id="b2", cohort_size=50, seed=1)
    await repository.complete_batch_run(
        test_db,
        batch_id="b2",
        naive_summary={"recovered_rupees": 100.0},
        mandateops_summary={"recovered_rupees": 150.0},
        executive_summary_text="Test summary.",
    )
    batch = await repository.get_batch_run(test_db, "b2")
    assert batch["status"] == "completed"
    assert batch["naive_summary"]["recovered_rupees"] == 100.0
    assert batch["mandateops_summary"]["recovered_rupees"] == 150.0
    assert batch["executive_summary_text"] == "Test summary."


async def test_save_and_get_outcomes_roundtrip(test_db):
    records = generate_cohort(n=50, seed=5)
    result = run_naive(records, seed=5)

    decline_texts = {r.mandate.id: r.initial_decline_text for r in records}
    classified_by = {r.mandate.id: "fallback_rule_engine" for r in records}
    names = {r.mandate.id: r.mandate.subscriber_name for r in records}

    await repository.save_outcomes(
        test_db,
        batch_id="b3",
        strategy="naive",
        outcomes=result.outcomes,
        decline_texts=decline_texts,
        classified_by=classified_by,
        subscriber_names=names,
    )

    fetched = await repository.get_outcomes(test_db, batch_id="b3", strategy="naive", limit=100)
    assert len(fetched) == 50

    single = await repository.get_outcome_by_mandate(
        test_db, batch_id="b3", strategy="naive", mandate_id=records[0].mandate.id
    )
    assert single is not None
    assert single["mandate_id"] == records[0].mandate.id


async def test_save_and_get_simulation_events_roundtrip(test_db):
    records = generate_cohort(n=30, seed=7)
    result = run_mandateops(records, get_scorer(), seed=7)

    await repository.save_simulation_events(
        test_db, batch_id="b4", strategy="mandateops", events=result.events
    )
    fetched = await repository.get_simulation_events(
        test_db, batch_id="b4", strategy="mandateops", limit=1000
    )
    assert len(fetched) == len(result.events)
    assert fetched[0]["sequence"] == 0


async def test_audit_events_persist_and_verify_intact(test_db):
    entries = [
        {
            "actor_layer": "deterministic",
            "event_type": "ATTEMPT_SCHEDULED",
            "mandate_id": "m1",
            "cycle_id": "c1",
            "detail": {"foo": "bar"},
        }
        for _ in range(5)
    ]
    await repository.append_audit_events(test_db, batch_id="b5", entries=entries)
    events = await repository.get_audit_events(test_db, "b5")
    assert len(events) == 5

    valid, bad_sequence = verify_chain(events)
    assert valid is True
    assert bad_sequence is None


async def test_audit_events_across_multiple_append_calls_stay_chained(test_db):
    """Appending in two separate calls (simulating two batches writing at
    different times) must still produce one continuous, valid chain.
    """
    first_batch = [
        {"actor_layer": "deterministic", "event_type": "A", "mandate_id": None, "cycle_id": None, "detail": {}}
        for _ in range(3)
    ]
    second_batch = [
        {"actor_layer": "statistical", "event_type": "B", "mandate_id": None, "cycle_id": None, "detail": {}}
        for _ in range(3)
    ]
    await repository.append_audit_events(test_db, batch_id="b6", entries=first_batch)
    await repository.append_audit_events(test_db, batch_id="b6", entries=second_batch)

    events = await repository.get_audit_events(test_db, "b6")
    assert len(events) == 6
    assert [e.sequence for e in events] == [0, 1, 2, 3, 4, 5]

    valid, bad_sequence = verify_chain(events)
    assert valid is True
    assert bad_sequence is None


async def test_delete_batch_run_removes_all_related_rows(test_db):
    records = generate_cohort(n=20, seed=13)
    result = run_naive(records, seed=13)
    decline_texts = {r.mandate.id: r.initial_decline_text for r in records}
    classified_by = {r.mandate.id: "fallback_rule_engine" for r in records}
    names = {r.mandate.id: r.mandate.subscriber_name for r in records}

    await repository.create_batch_run(test_db, batch_id="b8", cohort_size=20, seed=13)
    await repository.save_outcomes(
        test_db,
        batch_id="b8",
        strategy="naive",
        outcomes=result.outcomes,
        decline_texts=decline_texts,
        classified_by=classified_by,
        subscriber_names=names,
    )
    await repository.save_simulation_events(
        test_db, batch_id="b8", strategy="naive", events=result.events
    )
    await repository.append_audit_events(
        test_db,
        batch_id="b8",
        entries=[{"actor_layer": "deterministic", "event_type": "X", "mandate_id": None, "cycle_id": None, "detail": {}}],
    )

    deleted = await repository.delete_batch_run(test_db, "b8")
    assert deleted is True

    assert await repository.get_batch_run(test_db, "b8") is None
    assert await repository.get_outcomes(test_db, batch_id="b8", strategy="naive") == []
    assert await repository.get_simulation_events(test_db, batch_id="b8") == []
    assert await repository.get_audit_events(test_db, "b8") == []


async def test_delete_batch_run_returns_false_for_unknown_id(test_db):
    deleted = await repository.delete_batch_run(test_db, "does-not-exist")
    assert deleted is False


async def test_tampering_persisted_audit_row_is_detected(test_db):
    entries = [
        {"actor_layer": "deterministic", "event_type": "A", "mandate_id": None, "cycle_id": None, "detail": {"n": i}}
        for i in range(4)
    ]
    await repository.append_audit_events(test_db, batch_id="b7", entries=entries)

    # Simulate direct tampering with the underlying row.
    await test_db.execute(
        "UPDATE audit_events SET detail_json = ? WHERE batch_id = ? AND sequence = ?",
        ('{"n": 9999}', "b7", 2),
    )
    await test_db.commit()

    events = await repository.get_audit_events(test_db, "b7")
    valid, bad_sequence = verify_chain(events)
    assert valid is False
    assert bad_sequence == 2
