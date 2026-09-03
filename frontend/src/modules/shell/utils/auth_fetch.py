"""Authenticated httpx requests (server-side — Rio Python backend)."""

from __future__ import annotations

import typing as t

import httpx


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
