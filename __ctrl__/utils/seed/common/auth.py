"""Auth helpers: parse .env, login, and idempotent user lookup/creation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .api_client import ApiClient, ApiError


@dataclass
class AuthSession:
    client: ApiClient
    user_id: str
    email: str
    access_token: str


def load_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        raise FileNotFoundError(f"env file not found: {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        key, _, val = s.partition("=")
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def login(client: ApiClient, email: str, password: str) -> AuthSession:
    data = client.post(
        "/api/v1/base/login/access-token",
        form={"username": email, "password": password},
        timeout=180,
    )
    token = data["access_token"]
    authed = client.with_token(token)
    me = authed.get("/api/v1/base/login/me")
    return AuthSession(
        client=authed,
        user_id=str(me["id"]),
        email=me.get("email") or email,
        access_token=token,
    )


def list_users(client: ApiClient) -> list[dict[str, Any]]:
    """All users via the paginated superuser listing."""
    users: list[dict[str, Any]] = []
    skip = 0
    page_size = 100
    while True:
        page = client.get(
            "/api/v1/base/users/admin", query={"skip": skip, "limit": page_size}
        )
        rows = page.get("data") if isinstance(page, dict) else page
        rows = rows or []
        users.extend(rows)
        if len(rows) < page_size:
            return users
        skip += page_size


def find_user_by_email(client: ApiClient, email: str) -> dict[str, Any] | None:
    wanted = email.lower()
    for u in list_users(client):
        if str(u.get("email", "")).lower() == wanted:
            return u
    return None


def ensure_user(
    client: ApiClient,
    *,
    email: str,
    password: str,
    full_name: str | None = None,
    is_superuser: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Return (user, created). Existing users are left untouched."""
    existing = find_user_by_email(client, email)
    if existing is not None:
        return existing, False
    body: dict[str, Any] = {
        "email": email,
        "password": password,
        "is_active": True,
        "is_superuser": is_superuser,
    }
    if full_name:
        body["full_name"] = full_name
    try:
        return client.post("/api/v1/base/users/admin", json_body=body), True
    except ApiError as exc:
        if exc.status == 400 and "already exists" in exc.body:
            found = find_user_by_email(client, email)
            if found is not None:
                return found, False
        raise
