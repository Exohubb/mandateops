"""Unit tests for app.core.audit — hash-chained audit log.

Verifies chain construction, tamper detection, and that verify_chain can
pinpoint exactly which sequence number was tampered with.
"""

from datetime import datetime, timedelta

from app.core.audit import GENESIS_HASH, build_event, verify_chain


def _make_chain(n: int) -> list:
    events = []
    prev_hash = GENESIS_HASH
    base_time = datetime(2026, 1, 1, 0, 0)
    for i in range(n):
        event = build_event(
            event_id=f"evt-{i}",
            sequence=i,
            actor_layer="deterministic",
            event_type="ATTEMPT_SCHEDULED",
            mandate_id="mandate-1",
            cycle_id="cycle-1",
            detail={"attempt_number": i + 1},
            prev_hash=prev_hash,
            timestamp=base_time + timedelta(minutes=i),
        )
        events.append(event)
        prev_hash = event.this_hash
    return events


def test_first_event_chains_from_genesis() -> None:
    events = _make_chain(1)
    assert events[0].prev_hash == GENESIS_HASH


def test_chain_of_events_link_correctly() -> None:
    events = _make_chain(5)
    for i in range(1, len(events)):
        assert events[i].prev_hash == events[i - 1].this_hash


def test_verify_chain_passes_on_untampered_chain() -> None:
    events = _make_chain(10)
    ok, bad_sequence = verify_chain(events)
    assert ok is True
    assert bad_sequence is None


def test_verify_chain_detects_tampered_detail() -> None:
    events = _make_chain(10)
    # Tamper with event 5's detail without recomputing its hash — simulates
    # someone editing the underlying row directly in the database.
    tampered = events[5]
    tampered.detail = {"attempt_number": 9999}
    ok, bad_sequence = verify_chain(events)
    assert ok is False
    assert bad_sequence == 5


def test_verify_chain_detects_broken_link() -> None:
    events = _make_chain(10)
    # Break the link between event 3 and event 4.
    events[4].prev_hash = "deadbeef" * 8
    ok, bad_sequence = verify_chain(events)
    assert ok is False
    assert bad_sequence == 4


def test_identical_detail_produces_identical_hash_regardless_of_key_order() -> None:
    e1 = build_event(
        event_id="a",
        sequence=0,
        actor_layer="deterministic",
        event_type="X",
        mandate_id="m",
        cycle_id="c",
        detail={"a": 1, "b": 2},
        prev_hash=GENESIS_HASH,
        timestamp=datetime(2026, 1, 1),
    )
    e2 = build_event(
        event_id="b",
        sequence=0,
        actor_layer="deterministic",
        event_type="X",
        mandate_id="m",
        cycle_id="c",
        detail={"b": 2, "a": 1},
        prev_hash=GENESIS_HASH,
        timestamp=datetime(2026, 1, 1),
    )
    assert e1.this_hash == e2.this_hash
