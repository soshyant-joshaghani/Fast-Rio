"""Dedicated login page."""

from __future__ import annotations

import rio

from src.modules.shell import APP_NAME
from src.modules.shell.authentication import Authentication


@rio.page(
    name="Login",
    url_segment="login",
)
class LoginPage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            rio.Text("Welcome to", style="dim", justify="center"),
            rio.Text(APP_NAME, style="heading1", justify="center"),
            rio.Card(
                rio.Column(
                    Authentication(),
                    spacing=1,
                    margin=2,
                ),
                min_width=22,
            ),
            spacing=1.5,
            align_x=0.5,
            align_y=0.5,
            grow_y=True,
        )
