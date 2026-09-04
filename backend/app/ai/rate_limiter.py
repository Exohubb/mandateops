"""A small in-process token-bucket rate limiter for outgoing Gemini calls.

No Redis, no external process — at this scale (a single backend instance,
free-tier RPM limits in the single digits to low double digits) an
in-memory limiter is the right amount of engineering. Its job is to make
sure a burst of activity (e.g. a judge repeatedly clicking the AI Copilot)
queues politely instead of tripping a 429 live on stage.
"""

from __future__ import annotations

import asyncio
import time


class TokenBucketRateLimiter:
    """Classic token-bucket: `capacity` tokens available at once, refilled
    at `refill_rate_per_sec`. `acquire()` blocks (async) until a token is
    available, so callers naturally serialize instead of bursting.
    """

    def __init__(self, capacity: int, refill_rate_per_sec: float) -> None:
        self.capacity = capacity
        self.refill_rate_per_sec = refill_rate_per_sec
        self._tokens = float(capacity)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate_per_sec)
        self._last_refill = now

    async def acquire(self) -> None:
        while True:
            async with self._lock:
                self._refill()
                if self._tokens >= 1:
                    self._tokens -= 1
                    return
                # Not enough tokens yet — compute how long until one frees up.
                wait_time = (1 - self._tokens) / self.refill_rate_per_sec
            await asyncio.sleep(max(wait_time, 0.01))


def rpm_to_limiter(requests_per_minute: int, burst_capacity: int | None = None) -> TokenBucketRateLimiter:
    """Convenience constructor from a free-tier RPM figure."""
    capacity = burst_capacity or max(1, requests_per_minute // 4) or 1
    return TokenBucketRateLimiter(
        capacity=capacity,
        refill_rate_per_sec=requests_per_minute / 60.0,
    )
