"""Persistent seed-key → remote UUID maps for idempotent upserts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .paths import STATE_ROOT


def state_name_for(base: str, api_base: str | None = None) -> str:
    """Build a state filename scoped to API host (avoids local/prod UUID collisions)."""
    if not api_base:
        return base
    host = urlparse(api_base).hostname or api_base
    host = re.sub(r"[^a-zA-Z0-9._-]+", "_", host)
    return f"{base}.{host}"


class SeedState:
    def __init__(self, name: str) -> None:
        STATE_ROOT.mkdir(parents=True, exist_ok=True)
        self.path = STATE_ROOT / f"{name}.json"
        self.data: dict[str, Any] = {}
        if self.path.is_file():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))

    def nested_get(self, *keys: str, default: Any = None) -> Any:
        cur: Any = self.data
        for k in keys:
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur

    def nested_set(self, *keys: str, value: Any) -> None:
        if not keys:
            raise ValueError("keys required")
        cur = self.data
        for k in keys[:-1]:
            nxt = cur.get(k)
            if not isinstance(nxt, dict):
                nxt = {}
                cur[k] = nxt
            cur = nxt
        cur[keys[-1]] = value

    def save(self) -> None:
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
