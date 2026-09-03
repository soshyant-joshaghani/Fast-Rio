"""Root layout with sidebar, navbar, and auth guard."""

from __future__ import annotations

import rio

from src import components as comps
from src.modules.shell.authentication import Authentication
from src.modules.shell.stores import auth as auth_store


class RootComponent(rio.Component):
    def build(self) -> rio.Component:
        if auth_store.is_loading(self.session):
            return rio.Column(
                rio.Spacer(),
                rio.Text("Restoring session…", style="dim", justify="center"),
                rio.Spacer(),
                grow_y=True,
            )

        if not auth_store.is_authenticated(self.session):
            return rio.Column(
                rio.Spacer(),
                rio.Card(
                    rio.Column(
                        Authentication(),
                        spacing=1,
                        margin=2,
                    ),
                    min_width=22,
                ),
                rio.Spacer(),
                grow_y=True,
                align_x=0.5,
            )

        return rio.Row(
            comps.Sidebar(),
            rio.Column(
                comps.Navbar(),
                rio.PageView(
                    grow_y=True,
                    margin=2,
                ),
                grow_y=True,
                grow_x=True,
            ),
            grow_y=True,
            proportions=[1, 5],
        )
