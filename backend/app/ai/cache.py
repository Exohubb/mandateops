"""Content-hash keyed cache for AI call results.

Every AI call result (classification, drafted message, executive summary)
is cached by a hash of its input. Identical input never calls Gemini twice
— this is both a rate-limit defense and, per BUILD-BLUEPRINT.md, "just good
engineering" worth calling out explicitly in the demo.

In-memory for the hackathon build (a single backend process, modest data
volume). The interface is small enough that swapping to a SQLite-backed
cache later is a drop-in change if ever needed.
"""

from __future__ import annotations

import hashlib
import json
import threading


def content_hash(*parts: str) -> str:
    """Stable hash over an ordered sequence of string parts."""
    payload = json.dumps(list(parts), separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class AICache:
    """Thread-safe in-memory cache keyed by content hash."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> str | None:
        with self._lock:
            value = self._store.get(key)
            if value is not None:
                self.hits += 1
            else:
                self.misses += 1
            return value

    def set(self, key: str, value: str) -> None:
        with self._lock:
            self._store[key] = value

    def stats(self) -> dict[str, int]:
        with self._lock:
            return {"hits": self.hits, "misses": self.misses, "size": len(self._store)}


# Module-level singleton — one cache shared across the whole backend process.
ai_cache = AICache()
