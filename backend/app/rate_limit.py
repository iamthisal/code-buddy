from collections import deque
from threading import Lock


class RateLimiter:
    def __init__(self, limit: int, window_seconds: float = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = {}
        self._lock = Lock()

    def allow(self, key: str, now: float) -> bool:
        if self.limit <= 0:
            return True
        with self._lock:
            if len(self._hits) > 1024:
                self._hits = {client: times for client, times in self._hits.items() if times and times[-1] > now - self.window_seconds}
            hits = self._hits.setdefault(key, deque())
            while hits and hits[0] <= now - self.window_seconds:
                hits.popleft()
            if len(hits) >= self.limit:
                return False
            hits.append(now)
            return True
