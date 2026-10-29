"""Shared HTTP helpers for talking to the FastAPI backend (server-side)."""

from __future__ import annotations

import typing as t

import httpx


class ApiError(Exception):
    def __init__(self, message: str, status: int) -> None:
        super().__init__(message)
        self.status = status


def format_api_error(detail: t.Any, fallback: str) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        parts: list[str] = []
        for item in detail:
            if isinstance(item, dict) and "msg" in item:
                parts.append(str(item["msg"]))
            else:
                parts.append(str(item))
        return ", ".join(parts)
    return fallback


async def auth_fetch(
    method: str,
    url: str,
    token: str,
    **kwargs: t.Any,
) -> httpx.Response:
    headers = dict(kwargs.pop("headers", {}))
    headers["Authorization"] = f"Bearer {token}"
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        return await client.request(method, url, headers=headers, **kwargs)
