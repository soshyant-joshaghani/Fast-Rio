"""Upsert demo users through the superuser Admin API (no raw SQL)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from utils.seed.common.api_client import ApiError
from utils.seed.common.auth import AuthSession, ensure_user
from utils.seed.common.paths import SEED_ROOT
from utils.seed.common.state import SeedState, state_name_for

USERS_JSON = SEED_ROOT / "users" / "users.json"


def load_users(path: Path | None = None) -> list[dict[str, Any]]:
    data = json.loads((path or USERS_JSON).read_text(encoding="utf-8"))
    return list(data.get("users") or [])


def seed_users(
    session: AuthSession,
    *,
    purge: bool = False,
    api_base: str | None = None,
    users_path: Path | None = None,
) -> dict[str, int]:
    client = session.client
    state = SeedState(state_name_for("users", api_base))
    rows = load_users(users_path)

    if purge:
        deleted = 0
        for row in rows:
            key = str(row["key"])
            user_id = state.nested_get("users", key)
            if not user_id:
                continue
            if user_id == session.user_id:
                print(f"  skip purge {key} (is the logged-in user)")
                continue
            try:
                client.delete(f"/api/v1/base/users/{user_id}/admin")
                deleted += 1
                print(f"  purge {row['email']}")
            except ApiError as exc:
                if exc.status != 404:
                    raise
            state.data.get("users", {}).pop(key, None)
        state.save()
        print(f"seed users: purged={deleted}")
        return {"created": 0, "existing": 0, "purged": deleted}

    created = 0
    existing = 0
    for row in rows:
        key = str(row["key"])
        user, was_created = ensure_user(
            client,
            email=str(row["email"]),
            password=str(row["password"]),
            full_name=row.get("full_name"),
            is_superuser=bool(row.get("is_superuser", False)),
        )
        state.nested_set("users", key, value=str(user["id"]))
        if was_created:
            created += 1
            print(f"  create {row['email']} -> {user['id']}")
        else:
            existing += 1
            print(f"  exists {row['email']} -> {user['id']}")

    state.save()
    print(f"seed users: created={created} existing={existing}")
    return {"created": created, "existing": existing, "purged": 0}
