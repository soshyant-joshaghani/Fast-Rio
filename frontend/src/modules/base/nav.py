"""Shared dashboard navigation items."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NavItem:
    label: str
    path: str
    superuser_only: bool = False


NAV_ITEMS: tuple[NavItem, ...] = (
    NavItem("Dashboard", "/"),
    NavItem("Sample Notes", "/sample/notes"),
    NavItem("Admin", "/admin", superuser_only=True),
)
