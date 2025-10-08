"""简单的线程安全 TTL 缓存工具。"""

from __future__ import annotations

import threading
import time
from typing import Any, Hashable, Optional


class TTLCache:
    """支持过期淘汰的轻量缓存。"""

    def __init__(self, ttl_seconds: int = 300) -> None:
        self._ttl = ttl_seconds
        self._data: dict[Hashable, tuple[float, Any]] = {}
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: Hashable) -> Optional[Any]:
        now = time.time()
        with self._lock:
            item = self._data.get(key)
            if not item:
                self._misses += 1
                return None

            expires_at, value = item
            if expires_at < now:
                self._data.pop(key, None)
                self._misses += 1
                return None

            self._hits += 1
            return value

    def set(self, key: Hashable, value: Any) -> None:
        expires_at = time.time() + self._ttl
        with self._lock:
            self._data[key] = (expires_at, value)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()
            self._hits = 0
            self._misses = 0

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "ttl": self._ttl,
                "size": len(self._data),
                "hits": self._hits,
                "misses": self._misses,
            }
