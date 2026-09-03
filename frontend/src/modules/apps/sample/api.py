"""HTTP client for the sample notes API."""

from __future__ import annotations

import dataclasses
import typing as t

import httpx

from src.config.backend import API_BASE_URL
from src.modules.shell.utils.api_error import ApiError
from src.modules.shell.utils.auth_api import format_api_error
from src.modules.shell.utils.auth_fetch import auth_fetch


@dataclasses.dataclass(frozen=True)
class Note:
    id: str
    title: str
    content: str
    owner_id: str
    created_at: str
    updated_at: str


def _parse_note(data: dict[str, t.Any]) -> Note:
    return Note(
        id=str(data["id"]),
        title=data["title"],
        content=data.get("content", ""),
        owner_id=str(data["owner_id"]),
        created_at=str(data["created_at"]),
        updated_at=str(data["updated_at"]),
    )


def _raise_api_error(res: httpx.Response, fallback: str) -> None:
    try:
        body = res.json()
    except Exception:
        body = {}
    raise ApiError(format_api_error(body.get("detail"), fallback), res.status_code)


async def list_notes(token: str) -> list[Note]:
    res = await auth_fetch("GET", f"{API_BASE_URL}/sample/notes", token)
    if res.status_code >= 400:
        _raise_api_error(res, f"Failed to load notes ({res.status_code})")
    return [_parse_note(item) for item in res.json()]


async def create_note(token: str, title: str, content: str) -> Note:
    res = await auth_fetch(
        "POST",
        f"{API_BASE_URL}/sample/notes",
        token,
        json={"title": title, "content": content},
    )
    if res.status_code >= 400:
        _raise_api_error(res, f"Failed to create note ({res.status_code})")
    return _parse_note(res.json())


async def update_note(
    token: str,
    note_id: str,
    *,
    title: str | None = None,
    content: str | None = None,
) -> Note:
    payload: dict[str, str] = {}
    if title is not None:
        payload["title"] = title
    if content is not None:
        payload["content"] = content
    res = await auth_fetch(
        "PATCH",
        f"{API_BASE_URL}/sample/notes/{note_id}",
        token,
        json=payload,
    )
    if res.status_code >= 400:
        _raise_api_error(res, f"Failed to update note ({res.status_code})")
    return _parse_note(res.json())


async def delete_note(token: str, note_id: str) -> None:
    res = await auth_fetch("DELETE", f"{API_BASE_URL}/sample/notes/{note_id}", token)
    if res.status_code >= 400:
        _raise_api_error(res, f"Failed to delete note ({res.status_code})")
