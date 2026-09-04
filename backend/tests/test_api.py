"""End-to-end API tests using an in-process ASGI client against a temporary
SQLite database. Exercises the full request path: FastAPI route -> ORM-free
repository -> real SQLite file -> back through the response model.
"""

from __future__ import annotations

import httpx
import pytest_asyncio

from app.config import Settings, get_settings
import app.db.connection as db_connection
from app.main import app


@pytest_asyncio.fixture
async def client(tmp_path, monkeypatch):
    db_path = str(tmp_path / "api_test.db")

    def _fake_settings() -> Settings:
        return Settings(
            gemini_api_key="",
            database_path=db_path,
            cors_origins="http://localhost:5173",
        )

    monkeypatch.setattr("app.db.connection.get_settings", _fake_settings)
    monkeypatch.setattr("app.main.get_settings", _fake_settings)
    get_settings.cache_clear()

    # httpx.ASGITransport does not trigger FastAPI's lifespan handler, so
    # the database must be initialized explicitly here rather than relying
    # on app startup.
    await db_connection.init_db()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await db_connection.close_db()


async def test_health_endpoint(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["gemini_configured"] is False


async def test_run_small_batch_end_to_end(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/batches", json={"cohort_size": 100, "seed": 1})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    batch_id = body["batch_id"]
    assert batch_id.startswith("batch-")

    # Fetch the batch back.
    get_response = await client.get(f"/api/batches/{batch_id}")
    assert get_response.status_code == 200
    batch = get_response.json()
    assert batch["naive_summary"]["total_mandates"] == 100
    assert batch["mandateops_summary"]["total_mandates"] == 100
    assert len(batch["executive_summary_text"]) > 0


async def test_get_outcomes_for_batch(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/batches", json={"cohort_size": 60, "seed": 2})
    batch_id = response.json()["batch_id"]

    outcomes_response = await client.get(f"/api/batches/{batch_id}/outcomes/mandateops")
    assert outcomes_response.status_code == 200
    outcomes = outcomes_response.json()
    assert len(outcomes) == 60


async def test_get_outcomes_rejects_invalid_strategy(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/batches", json={"cohort_size": 20, "seed": 3})
    batch_id = response.json()["batch_id"]

    bad_response = await client.get(f"/api/batches/{batch_id}/outcomes/not_a_strategy")
    assert bad_response.status_code == 400


async def test_get_batch_404_for_unknown_id(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/batches/does-not-exist")
    assert response.status_code == 404


async def test_mandate_detail_endpoint(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/batches", json={"cohort_size": 40, "seed": 4})
    batch_id = response.json()["batch_id"]

    outcomes = (await client.get(f"/api/batches/{batch_id}/outcomes/mandateops")).json()
    mandate_id = outcomes[0]["mandate_id"]

    detail_response = await client.get(f"/api/batches/{batch_id}/mandate/{mandate_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["naive"]["mandate_id"] == mandate_id
    assert detail["mandateops"]["mandate_id"] == mandate_id
    assert isinstance(detail["events"], list)


async def test_audit_trail_and_verify_chain(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/batches", json={"cohort_size": 80, "seed": 5})
    batch_id = response.json()["batch_id"]

    audit_response = await client.get(f"/api/audit/{batch_id}")
    assert audit_response.status_code == 200
    events = audit_response.json()
    assert len(events) > 0

    verify_response = await client.post(f"/api/audit/{batch_id}/verify")
    assert verify_response.status_code == 200
    verify_body = verify_response.json()
    assert verify_body["valid"] is True
    assert verify_body["first_invalid_sequence"] is None
    assert verify_body["total_events"] == len(events) or verify_body["total_events"] >= len(events)


async def test_copilot_ask_degrades_gracefully_without_api_key(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/batches", json={"cohort_size": 30, "seed": 6})
    batch_id = response.json()["batch_id"]

    ask_response = await client.post(
        "/api/copilot/ask", json={"batch_id": batch_id, "question": "How many mandates recovered?"}
    )
    assert ask_response.status_code == 200
    body = ask_response.json()
    assert body["used_fallback"] is True
    assert len(body["answer"]) > 0


async def test_heatmap_endpoint(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/stats/heatmap/insufficient_funds")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "shrunk_probability" in data[0]
    assert "sufficient_support" in data[0]


async def test_ai_judgment_table_endpoint(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/stats/ai-judgment-table")
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 6
    assert all({"decision", "made_by", "why"} <= set(row.keys()) for row in rows)


async def test_list_batches_endpoint(client: httpx.AsyncClient) -> None:
    await client.post("/api/batches", json={"cohort_size": 20, "seed": 10})
    await client.post("/api/batches", json={"cohort_size": 20, "seed": 11})

    response = await client.get("/api/batches")
    assert response.status_code == 200
    batches = response.json()
    assert len(batches) >= 2


async def test_delete_batch_endpoint(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/batches", json={"cohort_size": 20, "seed": 20})
    batch_id = response.json()["batch_id"]

    delete_response = await client.delete(f"/api/batches/{batch_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"batch_id": batch_id, "deleted": True}

    get_response = await client.get(f"/api/batches/{batch_id}")
    assert get_response.status_code == 404


async def test_delete_batch_endpoint_404_for_unknown_id(client: httpx.AsyncClient) -> None:
    response = await client.delete("/api/batches/does-not-exist")
    assert response.status_code == 404
