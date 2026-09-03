"""Shell navbar with theme toggle and logout."""

from __future__ import annotations

import rio

from src.modules.shell.stores import auth as auth_store
from src.modules.shell.stores.auth import AuthUser
from src.modules.shell.stores.theme import is_dark, toggle_theme


class Navbar(rio.Component):
    def _logout(self) -> None:
        auth_store.apply_logout(self.session)
        self.session.navigate_to("/login")

    def _toggle_theme(self) -> None:
        toggle_theme(self.session)

    def build(self) -> rio.Component:
        right: rio.Component = rio.Spacer()
        if auth_store.is_authenticated(self.session):
            try:
                user = self.session[AuthUser]
            except KeyError:
                user = auth_store.settings_to_user(self.session[auth_store.AuthSettings])
            if user is not None:
                role = "SuperAdmin" if user.is_superuser else "User"
                right = rio.Row(
                    rio.Button(
                        "Light" if is_dark(self.session) else "Dark",
                        on_press=self._toggle_theme,
                        style="minor",
                    ),
                    rio.Column(
                        rio.Text(user.email, justify="right"),
                        rio.Text(role, style="dim", justify="right"),
                        spacing=0.2,
                        align_x=1,
                    ),
                    rio.Button("Log out", on_press=self._logout, color="danger"),
                    spacing=0.8,
                    align_y=0.5,
                )

        return rio.Card(
            rio.Row(
                rio.Spacer(),
                right,
                margin=1.2,
            ),
            color="background",
        )
