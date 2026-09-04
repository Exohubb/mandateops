"""Simulation event model.

A SimulationEvent is a lightweight, timestamped record of one thing that
happened during a batch run — separate from AuditEvent (app.core.models),
which is the permanent hash-chained record. SimulationEvents are what the
WebSocket streams to the frontend for the live event feed
(BUILD-BLUEPRINT.md section 6.3); a subset of them also get written to the
audit log via app.core.audit.build_event so the two stay consistent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class SimulationEvent:
    """One event produced during a simulated batch run."""

    timestamp: datetime
    mandate_id: str
    cycle_id: str
    event_type: str
    actor_layer: str  # ActorLayer value
    detail: dict[str, Any] = field(default_factory=dict)
