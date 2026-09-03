"""Dashboard sidebar navigation."""

from __future__ import annotations

import rio

from src.modules.shell import APP_NAME
from src.modules.shell.nav import NAV_ITEMS
from src.modules.shell.stores import auth as auth_store
from src.modules.shell.stores.auth import AuthUser


class Sidebar(rio.Component):
    def build(self) -> rio.Component:
        user: AuthUser | None = None
        if auth_store.is_authenticated(self.session):
            try:
                user = self.session[AuthUser]
            except KeyError:
                user = auth_store.settings_to_user(self.session[auth_store.AuthSettings])

        nav_links: list[rio.Component] = [
            rio.Text("Menu", style="heading3"),
        ]
        for item in NAV_ITEMS:
            if item.superuser_only and not (user and user.is_superuser):
                continue
            nav_links.append(rio.Link(item.label, item.path))

        return rio.Card(
            rio.Column(
                rio.Text("DASHBOARD", style="dim"),
                rio.Text(APP_NAME, style="heading2"),
                *nav_links,
                rio.Spacer(),
                rio.Text("Fast-Rio From FoxG", style="dim"),
                spacing=0.8,
                margin=1.2,
            ),
            min_width=14,
            color="neutral",
        )
