"""JSON read-cache helpers. Soft-degrade when Redis is unavailable (slim)."""

from __future__ import annotations

import json
from typing import Any

from redis.exceptions import RedisError

from app.core.redis import try_get_redis


def cache_get(key: str) -> dict[str, Any] | list[Any] | None:
    client = try_get_redis()
    if client is None:
        return None
    try:
        raw = client.get(key)
    except (RedisError, OSError, TimeoutError):
        return None
    if raw is None:
        return None
    try:
        data = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return None
    if isinstance(data, (dict, list)):
        return data
    return None


def cache_set(key: str, value: Any, ttl_s: int) -> bool:
    client = try_get_redis()
    if client is None:
        return False
    try:
        payload = json.dumps(value, default=str, separators=(",", ":"))
        client.set(key, payload, ex=max(1, int(ttl_s)))
        return True
    except (RedisError, OSError, TimeoutError, TypeError):
        return False


def cache_delete(*keys: str) -> int:
    if not keys:
        return 0
    client = try_get_redis()
    if client is None:
        return 0
    try:
        return int(client.delete(*keys))
    except (RedisError, OSError, TimeoutError):
        return 0


def cache_delete_prefix(prefix: str) -> int:
    """Delete keys matching ``prefix*`` via SCAN (safe for production)."""
    if not prefix:
        return 0
    client = try_get_redis()
    if client is None:
        return 0
    deleted = 0
    pattern = f"{prefix}*"
    try:
        for key in client.scan_iter(match=pattern, count=200):
            deleted += int(client.delete(key))
    except (RedisError, OSError, TimeoutError):
        return deleted
    return deleted
