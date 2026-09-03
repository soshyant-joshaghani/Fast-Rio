"""HTTP client for SuperAdmin user CRUD."""

from __future__ import annotations

import dataclasses
import typing as t

from src.config.backend import API_BASE_URL
from src.modules.shell.utils.auth_api import format_api_error
from src.modules.shell.utils.auth_fetch import auth_fetch


@dataclasses.dataclass(frozen=True)
class User:
    id: str
    email: str
    full_name: str | None
    is_active: bool
    is_superuser: bool


def _parse_user(data: dict[str, t.Any]) -> User:
    return User(
        id=str(data["id"]),
        email=data["email"],
        full_name=data.get("full_name"),
        is_active=bool(data.get("is_active", True)),
        is_superuser=bool(data.get("is_superuser", False)),
    )


async def list_users(token: str, *, skip: int = 0, limit: int = 100) -> list[User]:
    res = await auth_fetch(
        "GET",
        f"{API_BASE_URL}/base/users/admin",
        token,
        params={"skip": skip, "limit": limit},
    )
    if res.status_code >= 400:
        try:
            body = res.json()
        except Exception:
            body = {}
        raise RuntimeError(format_api_error(body.get("detail"), "Failed to load users"))
    body = res.json()
    return [_parse_user(item) for item in body["data"]]


async def create_user(
    token: str,
    *,
    email: str,
    password: str,
    full_name: str | None = None,
    is_active: bool = False,
    is_superuser: bool = False,
) -> User:
    payload: dict[str, t.Any] = {
        "email": email,
        "password": password,
        "is_active": is_active,
        "is_superuser": is_superuser,
    }
    if full_name:
        payload["full_name"] = full_name
    res = await auth_fetch(
        "POST",
        f"{API_BASE_URL}/base/users/admin",
        token,
        json=payload,
    )
    if res.status_code >= 400:
        try:
            body = res.json()
        except Exception:
            body = {}
        raise RuntimeError(format_api_error(body.get("detail"), "Failed to create user"))
    return _parse_user(res.json())


async def update_user(
    token: str,
    user_id: str,
    *,
    email: str | None = None,
    full_name: str | None = None,
    password: str | None = None,
    is_active: bool | None = None,
    is_superuser: bool | None = None,
) -> User:
    payload: dict[str, t.Any] = {}
    if email is not None:
        payload["email"] = email
    if full_name is not None:
        payload["full_name"] = full_name
    if password is not None:
        payload["password"] = password
    if is_active is not None:
        payload["is_active"] = is_active
    if is_superuser is not None:
        payload["is_superuser"] = is_superuser
    res = await auth_fetch(
        "PATCH",
        f"{API_BASE_URL}/base/users/{user_id}/admin",
        token,
        json=payload,
    )
    if res.status_code >= 400:
        try:
            body = res.json()
        except Exception:
            body = {}
        raise RuntimeError(format_api_error(body.get("detail"), "Failed to update user"))
    return _parse_user(res.json())


async def delete_user(token: str, user_id: str) -> None:
    res = await auth_fetch(
        "DELETE",
        f"{API_BASE_URL}/base/users/{user_id}/admin",
        token,
    )
    if res.status_code >= 400:
        try:
            body = res.json()
        except Exception:
            body = {}
        raise RuntimeError(format_api_error(body.get("detail"), "Failed to delete user"))
