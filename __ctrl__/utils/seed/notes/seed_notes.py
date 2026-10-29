"""Seed sample notes, each created as its owning demo user (notes are owner-scoped)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from utils.seed.common.api_client import ApiClient, ApiError
from utils.seed.common.auth import AuthSession, login
from utils.seed.common.paths import SEED_ROOT
from utils.seed.common.state import SeedState, state_name_for
from utils.seed.users.seed_users import load_users

NOTES_JSON = SEED_ROOT / "notes" / "notes.json"


def load_notes(path: Path | None = None) -> list[dict[str, Any]]:
    data = json.loads((path or NOTES_JSON).read_text(encoding="utf-8"))
    return list(data.get("notes") or [])


def seed_notes(
    session: AuthSession,
    *,
    purge: bool = False,
    api_base: str | None = None,
    notes_path: Path | None = None,
    users_path: Path | None = None,
) -> dict[str, int]:
    """Create each note once (matched by owner + title). Users must be seeded first."""
    users = {str(u["key"]): u for u in load_users(users_path)}
    state = SeedState(state_name_for("notes", api_base))
    sessions: dict[str, ApiClient] = {}

    def client_for(user_key: str) -> ApiClient:
        if user_key not in sessions:
            cfg = users.get(user_key)
            if cfg is None:
                raise SystemExit(f"notes.json references unknown user key {user_key!r}")
            try:
                sessions[user_key] = login(
                    ApiClient(session.client._display_url),
                    cfg["email"],
                    cfg["password"],
                ).client
            except ApiError as exc:
                raise SystemExit(
                    f"cannot log in as {cfg['email']} ({exc.status}); "
                    "run `seed users` first"
                ) from exc
        return sessions[user_key]

    rows = load_notes(notes_path)

    if purge:
        deleted = 0
        for row in rows:
            note_key = f"{row['user']}/{row['title']}"
            note_id = state.nested_get("notes", note_key)
            if not note_id:
                continue
            try:
                client_for(str(row["user"])).delete(f"/api/v1/sample/notes/{note_id}")
                deleted += 1
                print(f"  purge {note_key}")
            except ApiError as exc:
                if exc.status != 404:
                    raise
            except SystemExit:
                # owner already gone (users purged first): its notes went with it
                pass
            state.data.get("notes", {}).pop(note_key, None)
        state.save()
        print(f"seed notes: purged={deleted}")
        return {"created": 0, "existing": 0, "purged": deleted}

    created = 0
    existing = 0
    for row in rows:
        user_key = str(row["user"])
        title = str(row["title"])
        client = client_for(user_key)
        mine = client.get("/api/v1/sample/notes") or []
        match = next((n for n in mine if n.get("title") == title), None)
        note_key = f"{user_key}/{title}"
        if match is not None:
            existing += 1
            state.nested_set("notes", note_key, value=str(match["id"]))
            print(f"  exists {note_key}")
            continue
        made = client.post(
            "/api/v1/sample/notes",
            json_body={"title": title, "content": str(row.get("content") or "")},
            expect={200, 201},
        )
        created += 1
        state.nested_set("notes", note_key, value=str(made["id"]))
        print(f"  create {note_key} -> {made['id']}")

    state.save()
    print(f"seed notes: created={created} existing={existing}")
    return {"created": created, "existing": existing, "purged": 0}
