"""
Redis Cache Operations

Memory and caching with TTL support.
Students implement this in Week 5.
"""

from typing import Optional, Any
import json
from config import settings


# Redis connection placeholder
_redis_client = None


def get_redis_connection():
    """
    Get a Redis connection.

    TODO: Implement in Week 5 using redis-py.
    """
    global _redis_client

    # Placeholder - implement actual connection
    # import redis
    # if _redis_client is None:
    #     _redis_client = redis.from_url(settings.REDIS_URL)
    # return _redis_client

    print("[PLACEHOLDER] Would connect to Redis")
    return None


def cache_get(key: str) -> Optional[Any]:
    """
    Get a value from cache.

    Args:
        key: Cache key

    Returns:
        Cached value or None
    """
    # TODO: Implement in Week 5
    # r = get_redis_connection()
    # value = r.get(key)
    # if value:
    #     return json.loads(value)
    # return None

    print(f"[PLACEHOLDER] Would get cache key: {key}")
    return None


def cache_set(
    key: str,
    value: Any,
    ttl_seconds: Optional[int] = None
) -> bool:
    """
    Set a value in cache with optional TTL.

    Args:
        key: Cache key
        value: Value to cache (will be JSON serialized)
        ttl_seconds: Time-to-live in seconds (default from settings)

    Returns:
        True if set successfully
    """
    if ttl_seconds is None:
        ttl_seconds = settings.MEMORY_TTL_SECONDS

    # TODO: Implement in Week 5
    # r = get_redis_connection()
    # r.setex(key, ttl_seconds, json.dumps(value))

    print(f"[PLACEHOLDER] Would set cache key: {key} (TTL: {ttl_seconds}s)")
    return True


def cache_delete(key: str) -> bool:
    """
    Delete a value from cache.

    Args:
        key: Cache key

    Returns:
        True if deleted (or didn't exist)
    """
    # TODO: Implement in Week 5
    # r = get_redis_connection()
    # r.delete(key)

    print(f"[PLACEHOLDER] Would delete cache key: {key}")
    return True


def cache_exists(key: str) -> bool:
    """
    Check if a key exists in cache.

    Args:
        key: Cache key

    Returns:
        True if key exists
    """
    # TODO: Implement in Week 5
    # r = get_redis_connection()
    # return r.exists(key) > 0

    print(f"[PLACEHOLDER] Would check cache key: {key}")
    return False


def cache_keys(pattern: str) -> list[str]:
    """
    Find keys matching a pattern.

    Args:
        pattern: Redis key pattern (e.g., "company:*")

    Returns:
        List of matching keys
    """
    # TODO: Implement in Week 5
    # r = get_redis_connection()
    # return [k.decode() for k in r.keys(pattern)]

    print(f"[PLACEHOLDER] Would search keys: {pattern}")
    return []


def cache_increment(key: str, amount: int = 1) -> int:
    """
    Increment a counter in cache.

    Useful for rate limiting (Week 10).

    Args:
        key: Cache key
        amount: Amount to increment by

    Returns:
        New counter value
    """
    # TODO: Implement in Week 5
    # r = get_redis_connection()
    # return r.incr(key, amount)

    print(f"[PLACEHOLDER] Would increment: {key} by {amount}")
    return amount


def cache_flush_pattern(pattern: str) -> int:
    """
    Delete all keys matching a pattern.

    Use with caution!

    Args:
        pattern: Redis key pattern

    Returns:
        Number of keys deleted
    """
    # TODO: Implement in Week 5
    # r = get_redis_connection()
    # keys = r.keys(pattern)
    # if keys:
    #     return r.delete(*keys)
    # return 0

    print(f"[PLACEHOLDER] Would flush pattern: {pattern}")
    return 0
