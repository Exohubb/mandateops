// Small TTL-backed sessionStorage helper.
//
// sessionStorage (not localStorage) is deliberate: it survives a page
// refresh and switching between tabs/routes within the SPA, but clears
// itself when the browser tab is actually closed — matching "cache the
// response for a while, not forever." A TTL on top means even a
// long-lived tab eventually forgets stale chat/simulation state rather
// than showing something from hours ago.

const DEFAULT_TTL_MS = 60 * 60 * 1000; // 1 hour

interface CacheEnvelope<T> {
  value: T;
  savedAt: number;
  ttlMs: number;
}

export function saveToCache<T>(key: string, value: T, ttlMs: number = DEFAULT_TTL_MS): void {
  try {
    const envelope: CacheEnvelope<T> = { value, savedAt: Date.now(), ttlMs };
    window.sessionStorage.setItem(key, JSON.stringify(envelope));
  } catch {
    // sessionStorage can throw in private-browsing / quota-exceeded cases —
    // losing the cache is an acceptable degradation, not worth crashing over.
  }
}

export function loadFromCache<T>(key: string): T | null {
  try {
    const raw = window.sessionStorage.getItem(key);
    if (!raw) return null;
    const envelope = JSON.parse(raw) as CacheEnvelope<T>;
    if (Date.now() - envelope.savedAt > envelope.ttlMs) {
      window.sessionStorage.removeItem(key);
      return null;
    }
    return envelope.value;
  } catch {
    return null;
  }
}

export function clearCache(key: string): void {
  try {
    window.sessionStorage.removeItem(key);
  } catch {
    // ignore
  }
}
