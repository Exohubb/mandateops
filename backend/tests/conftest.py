"""Shared pytest fixtures for API/DB integration tests.

Uses a temporary SQLite file per test (via tmp_path) rather than the real
app database, and monkeypatches app.config.get_settings so the app under
test never touches ./data/mandateops.db.
"""

from __future__ import annotations

import pytest
import pytest_asyncio

from app.config import Settings, get_settings
import app.db.connection as db_connection


@pytest_asyncio.fixture
async def test_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")

    def _fake_settings() -> Settings:
        return Settings(
            gemini_api_key="",
            database_path=db_path,
            cors_origins="http://localhost:5173",
        )

    monkeypatch.setattr("app.db.connection.get_settings", _fake_settings)
    get_settings.cache_clear()

    conn = await db_connection.init_db()
    yield conn
    await db_connection.close_db()
