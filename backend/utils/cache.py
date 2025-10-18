"""Optional external cache abstraction with Redis support.

This module provides an optional caching layer that uses Redis when
CACHE_ENABLED=true and REDIS_URL are set. Otherwise, it falls back
to direct factory function calls (no external caching).
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Callable, Optional

_CACHE_ENABLED = os.getenv("CACHE_ENABLED", "false").lower() in {"1", "true", "yes"}

try:
    import redis  # optional
except Exception:
    redis = None


class Cache:
    """External cache abstraction with Redis backend.

    Provides get-or-set caching with TTL support. Falls back to
    no-op mode when Redis is unavailable or disabled.

    Attributes:
        enabled: Whether external caching is active.

    Example:
        >>> cache = Cache()
        >>> def fetch_data():
        ...     return {"result": 42}
        >>> data = cache.get_or_set("mykey", 300, fetch_data)
    """

    def __init__(self):
        """Initialize cache with Redis connection if available."""
        self.enabled = _CACHE_ENABLED and redis is not None and os.getenv("REDIS_URL")
        self._client = redis.from_url(os.getenv("REDIS_URL")) if self.enabled else None

    def get_or_set(self, key: str, ttl: int, factory: Callable[[], Any]) -> Any:
        """Get cached value or compute and cache it.

        Args:
            key: Cache key string.
            ttl: Time-to-live in seconds.
            factory: Callable that produces the value if cache miss.

        Returns:
            Cached or freshly computed value.

        Example:
            >>> cache = Cache()
            >>> result = cache.get_or_set("expensive_op", 600, lambda: compute())
        """
        if not self.enabled:
            return factory()
        v = self._client.get(key)
        if v is not None:
            import json

            return json.loads(v)
        val = factory()
        import json

        self._client.setex(key, ttl, json.dumps(val))
        return val


_cache_singleton: Optional[Cache] = None


def get_cache() -> Cache:
    """Get the singleton Cache instance.

    Returns:
        Singleton Cache instance.

    Example:
        >>> cache = get_cache()
        >>> cache.enabled
        False  # if CACHE_ENABLED not set
    """
    global _cache_singleton
    if _cache_singleton is None:
        _cache_singleton = Cache()
    return _cache_singleton
