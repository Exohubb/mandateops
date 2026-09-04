"""SQLite connection management using aiosqlite.

One shared connection per process, opened at app startup and closed at
shutdown (see app/main.py's lifespan handler). WAL mode is enabled so reads
(dashboard polling) don't block writes (a batch run in progress) — important
on a single small EC2 instance where we can't just throw more DB processes
at contention.
"""

from __future__ import annotations

import os

import aiosqlite

from app.config import get_settings
from app.db.schema import CREATE_TABLES_SQL

_connection: aiosqlite.Connection | None = None


async def init_db() -> aiosqlite.Connection:
    """Open the SQLite connection (creating the data directory and file if
    needed) and ensure the schema exists. Safe to call once at startup.
    """
    global _connection
    settings = get_settings()
    db_path = settings.database_path
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    _connection = await aiosqlite.connect(db_path)
    _connection.row_factory = aiosqlite.Row
    await _connection.execute("PRAGMA journal_mode=WAL;")
    await _connection.execute("PRAGMA foreign_keys=ON;")
    await _connection.executescript(CREATE_TABLES_SQL)
    await _connection.commit()
    return _connection


async def close_db() -> None:
    global _connection
    if _connection is not None:
        await _connection.close()
        _connection = None


def get_db() -> aiosqlite.Connection:
    """Return the shared connection. Raises if init_db() has not run yet —
    that's a startup-ordering bug, not something to silently work around.
    """
    if _connection is None:
        raise RuntimeError("Database not initialized. Call init_db() at app startup.")
    return _connection
