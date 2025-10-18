"""Time-to-live cache with LRU eviction for detection results.

This module provides a generic TTL cache implementation that automatically
expires entries and evicts least-recently-used items when capacity is reached.
"""

from __future__ import annotations

import time
from collections import OrderedDict
from typing import Generic, Optional, Tuple, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class TTLCache(Generic[K, V]):
    """Time-to-live cache with LRU eviction policy.

    This cache stores key-value pairs with automatic expiration based on TTL
    (time-to-live). When the cache reaches maxsize, least-recently-used items
    are evicted. Expired items are automatically pruned and skipped during access.

    Attributes:
        maxsize: Maximum number of entries in the cache.
        ttl_sec: Time-to-live in seconds for each entry.

    Example:
        >>> cache = TTLCache[str, float](maxsize=100, ttl_sec=300)
        >>> cache.set("key1", 0.85)
        >>> value = cache.get("key1")
        >>> value
        0.85
    """

    def __init__(self, maxsize: int = 2048, ttl_sec: int = 600) -> None:
        """Initialize TTL cache.

        Args:
            maxsize: Maximum number of entries (default: 2048).
            ttl_sec: Time-to-live in seconds (default: 600).
        """
        self.maxsize = maxsize
        self.ttl_sec = ttl_sec

        # Store (value, expiry_time) tuples in OrderedDict for LRU
        self._cache: OrderedDict[K, Tuple[V, float]] = OrderedDict()

    def _is_expired(self, expiry_time: float) -> bool:
        """Check if an entry has expired.

        Args:
            expiry_time: Expiration timestamp.

        Returns:
            True if expired, False otherwise.
        """
        return time.time() > expiry_time

    def _prune_expired(self) -> None:
        """Remove all expired entries from the cache.

        This method iterates through the cache and removes entries whose
        TTL has expired. Called automatically during set operations.
        """
        current_time = time.time()
        expired_keys = [
            key
            for key, (_, expiry_time) in self._cache.items()
            if current_time > expiry_time
        ]

        for key in expired_keys:
            del self._cache[key]

    def _evict_lru(self) -> None:
        """Evict the least-recently-used entry.

        Removes the oldest entry (first item in OrderedDict) to make room
        for new entries when maxsize is reached.
        """
        if self._cache:
            self._cache.popitem(last=False)  # Remove first (oldest) item

    def get(self, key: K) -> Optional[V]:
        """Retrieve value from cache.

        Returns None if key doesn't exist or has expired. Expired entries
        are automatically removed. Accessing a key moves it to the end
        (marks as recently used) for LRU eviction.

        Args:
            key: Cache key to retrieve.

        Returns:
            Cached value or None if not found or expired.

        Example:
            >>> cache = TTLCache[str, float]()
            >>> cache.set("key1", 0.75)
            >>> cache.get("key1")
            0.75
            >>> cache.get("nonexistent")
            None
        """
        if key not in self._cache:
            return None

        value, expiry_time = self._cache[key]

        # Check if expired
        if self._is_expired(expiry_time):
            del self._cache[key]
            return None

        # Move to end (mark as recently used)
        self._cache.move_to_end(key)

        return value

    def set(self, key: K, value: V) -> None:
        """Store value in cache with TTL.

        If key already exists, updates the value and refreshes TTL.
        Prunes expired entries and evicts LRU items if cache is full.

        Args:
            key: Cache key.
            value: Value to store.

        Example:
            >>> cache = TTLCache[str, float]()
            >>> cache.set("key1", 0.85)
            >>> cache.set("key2", 0.65)
        """
        # Prune expired entries first
        self._prune_expired()

        # Calculate expiry time
        expiry_time = time.time() + self.ttl_sec

        # If key exists, remove it (will be re-added at end)
        if key in self._cache:
            del self._cache[key]

        # Evict LRU if at capacity
        while len(self._cache) >= self.maxsize:
            self._evict_lru()

        # Add new entry at end (most recently used)
        self._cache[key] = (value, expiry_time)

    def clear(self) -> None:
        """Clear all entries from the cache.

        Example:
            >>> cache = TTLCache[str, float]()
            >>> cache.set("key1", 0.75)
            >>> cache.clear()
            >>> cache.get("key1")
            None
        """
        self._cache.clear()

    def size(self) -> int:
        """Get current number of entries in cache.

        Note: May include expired entries that haven't been pruned yet.

        Returns:
            Number of entries currently in cache.

        Example:
            >>> cache = TTLCache[str, float]()
            >>> cache.set("key1", 0.75)
            >>> cache.size()
            1
        """
        return len(self._cache)

    def __contains__(self, key: K) -> bool:
        """Check if key exists in cache and is not expired.

        Args:
            key: Key to check.

        Returns:
            True if key exists and is not expired, False otherwise.

        Example:
            >>> cache = TTLCache[str, float]()
            >>> cache.set("key1", 0.75)
            >>> "key1" in cache
            True
            >>> "key2" in cache
            False
        """
        return self.get(key) is not None


# Type aliases for specific cache use cases
HeuristicCache = TTLCache[str, float]
"""Cache for heuristic detection scores.

Keys are raw text strings, values are normalized scores in [0, 1] range.
"""

EmbeddingCache = TTLCache[str, float]
"""Cache for embedding-based outlier scores.

Keys are raw text strings, values are normalized scores in [0, 1] range.
"""
