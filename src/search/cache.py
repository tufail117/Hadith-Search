"""Simple in-memory cache with TTL for search results."""

import re
import time
from typing import Dict, Any, Optional, List


class SearchCache:
    """In-memory cache for search results with TTL and LRU eviction."""

    def __init__(self, max_size: int = 10000, ttl_seconds: int = 86400):
        """Initialize cache.

        Args:
            max_size: Maximum number of cached entries.
            ttl_seconds: Time-to-live in seconds.
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._hits = 0
        self._misses = 0

    def _normalize_query(self, query: str) -> str:
        """Normalize query for consistent cache keys.

        Args:
            query: Raw query string.

        Returns:
            Normalized query string.
        """
        # Lowercase
        normalized = query.lower()
        # Remove punctuation
        normalized = re.sub(r'[^\w\s]', '', normalized)
        # Normalize whitespace
        normalized = ' '.join(normalized.split())
        return normalized

    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired.

        Args:
            entry: Cache entry with timestamp.

        Returns:
            True if expired.
        """
        return time.time() - entry["timestamp"] > self.ttl_seconds

    def _evict_oldest(self) -> None:
        """Remove oldest entry when cache is full."""
        if not self._cache:
            return

        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k]["timestamp"]
        )
        del self._cache[oldest_key]

    def get(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached results for a query.

        Args:
            query: Search query.

        Returns:
            Cached results or None if not found/expired.
        """
        key = self._normalize_query(query)

        if key in self._cache:
            entry = self._cache[key]
            if not self._is_expired(entry):
                self._hits += 1
                return entry["results"]
            else:
                # Remove expired entry
                del self._cache[key]

        self._misses += 1
        return None

    def set(self, query: str, results: List[Dict[str, Any]]) -> None:
        """Cache results for a query.

        Args:
            query: Search query.
            results: Search results to cache.
        """
        key = self._normalize_query(query)

        # Evict if at capacity
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._evict_oldest()

        self._cache[key] = {
            "results": results,
            "timestamp": time.time()
        }

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dict with cache stats.
        """
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate
        }


# Global cache instance
_cache: Optional[SearchCache] = None


def get_cache() -> SearchCache:
    """Get or create global cache instance."""
    global _cache
    if _cache is None:
        from src.config import CACHE_MAX_SIZE, CACHE_TTL_SECONDS
        _cache = SearchCache(max_size=CACHE_MAX_SIZE, ttl_seconds=CACHE_TTL_SECONDS)
    return _cache
