"""WebSocket endpoint for the live simulation view.

Per BUILD-BLUEPRINT.md section 6.3, the dashboard's centerpiece is watching
a batch run happen live rather than clicking refresh on a finished table.
Since run_naive/run_mandateops are fast, pure, synchronous computations
(no real wall-clock waiting), this endpoint runs the batch once and then
REPLAYS its already-computed events to the client at a controllable pace —
giving the same "watching it happen" experience without needing the actual
computation to be slow.
"""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.simulation.cohort import generate_cohort
from app.simulation.orchestrator import get_scorer
from app.simulation.runner import run_mandateops, run_naive

router = APIRouter()


@router.websocket("/ws/live-run")
async def live_run(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        config_raw = await websocket.receive_text()
        config = json.loads(config_raw) if config_raw else {}
        cohort_size = int(config.get("cohort_size", 1000))
        seed = int(config.get("seed", 2026))
        speed = float(config.get("speed", 50))  # events per tick

        records = generate_cohort(n=cohort_size, seed=seed)
        naive_result = run_naive(records, seed=seed + 1)
        mandateops_result = run_mandateops(records, get_scorer(), seed=seed + 1)

        await websocket.send_json(
            {
                "type": "run_started",
                "cohort_size": cohort_size,
                "total_naive_events": len(naive_result.events),
                "total_mandateops_events": len(mandateops_result.events),
            }
        )

        max_len = max(len(naive_result.events), len(mandateops_result.events))
        naive_recovered_so_far = 0.0
        mandateops_recovered_so_far = 0.0

        for i in range(0, max_len, max(1, int(speed))):
            naive_chunk = naive_result.events[i : i + int(speed)]
            mandateops_chunk = mandateops_result.events[i : i + int(speed)]

            for e in naive_chunk:
                if e.detail.get("success"):
                    naive_recovered_so_far += 1
            for e in mandateops_chunk:
                if e.detail.get("success"):
                    mandateops_recovered_so_far += 1

            await websocket.send_json(
                {
                    "type": "tick",
                    "naive_events": [
                        {
                            "event_type": e.event_type,
                            "mandate_id": e.mandate_id,
                            "actor_layer": e.actor_layer,
                            "detail": e.detail,
                            "timestamp": e.timestamp.isoformat(),
                        }
                        for e in naive_chunk
                    ],
                    "mandateops_events": [
                        {
                            "event_type": e.event_type,
                            "mandate_id": e.mandate_id,
                            "actor_layer": e.actor_layer,
                            "detail": e.detail,
                            "timestamp": e.timestamp.isoformat(),
                        }
                        for e in mandateops_chunk
                    ],
                    "naive_recovered_progress": naive_recovered_so_far,
                    "mandateops_recovered_progress": mandateops_recovered_so_far,
                }
            )
            await asyncio.sleep(0.05)

        await websocket.send_json(
            {
                "type": "run_completed",
                "naive_summary": naive_result.summary(),
                "mandateops_summary": mandateops_result.summary(),
            }
        )
    except WebSocketDisconnect:
        pass
