"""Sync Redis client with soft degrade for slim / unreachable Redis."""

from __future__ import annotations

import threading
import time
from functools import lru_cache

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings

# After a failed probe, skip reconnect attempts for this long (slim spam guard).
_NEGATIVE_TTL_S = 30.0

_lock = threading.Lock()
_unavailable_until: float = 0.0


@lru_cache
def get_redis() -> Redis:
    return Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=0.5)


def _mark_unavailable() -> None:
    global _unavailable_until
    with _lock:
        _unavailable_until = time.monotonic() + _NEGATIVE_TTL_S


def reset_redis_availability() -> None:
    """Test helper — clear negative cache and client singleton."""
    global _unavailable_until
    with _lock:
        _unavailable_until = 0.0
    get_redis.cache_clear()


def try_get_redis() -> Redis | None:
    """Return a live Redis client, or None when Redis is down / slim."""
    global _unavailable_until
    with _lock:
        if time.monotonic() < _unavailable_until:
            return None
    try:
        client = get_redis()
        client.ping()
        return client
    except (RedisError, OSError, TimeoutError):
        _mark_unavailable()
        return None
