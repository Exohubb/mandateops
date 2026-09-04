"""SQLite schema for MandateOps.

Raw SQL, no ORM — deliberate choice for a hackathon-scoped, single-instance
deployment (see BUILD-BLUEPRINT.md section 4.1): fewer moving parts, easier
to reason about on a 4GB/2vCPU box, and every query is visible and auditable
in this file rather than hidden behind a query builder.

One SQLite file holds everything. `init_db` is idempotent (CREATE TABLE IF
NOT EXISTS) so it's safe to call on every app startup.
"""

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS batch_runs (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    cohort_size INTEGER NOT NULL,
    seed INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'running',
    naive_summary_json TEXT,
    mandateops_summary_json TEXT,
    executive_summary_text TEXT
);

CREATE TABLE IF NOT EXISTS mandate_outcomes (
    batch_id TEXT NOT NULL,
    strategy TEXT NOT NULL,
    mandate_id TEXT NOT NULL,
    cycle_id TEXT NOT NULL,
    subscriber_name TEXT NOT NULL,
    bank TEXT NOT NULL,
    decline_category TEXT NOT NULL,
    decline_raw_text TEXT NOT NULL,
    final_state TEXT NOT NULL,
    attempts_used INTEGER NOT NULL,
    attempts_saved INTEGER NOT NULL,
    recovered INTEGER NOT NULL,
    recovered_amount_paise INTEGER NOT NULL,
    plan_amount_paise INTEGER NOT NULL,
    classified_by TEXT NOT NULL,
    PRIMARY KEY (batch_id, strategy, mandate_id)
);

CREATE INDEX IF NOT EXISTS idx_mandate_outcomes_batch_strategy
    ON mandate_outcomes (batch_id, strategy);

CREATE INDEX IF NOT EXISTS idx_mandate_outcomes_bank
    ON mandate_outcomes (batch_id, strategy, bank);

CREATE TABLE IF NOT EXISTS simulation_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL,
    strategy TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    mandate_id TEXT NOT NULL,
    cycle_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    actor_layer TEXT NOT NULL,
    detail_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_simulation_events_batch_strategy_seq
    ON simulation_events (batch_id, strategy, sequence);

CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    batch_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    actor_layer TEXT NOT NULL,
    event_type TEXT NOT NULL,
    mandate_id TEXT,
    cycle_id TEXT,
    detail_json TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    this_hash TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_events_batch_seq
    ON audit_events (batch_id, sequence);
"""
