"""Home / dashboard page — mirrors (dashboard)/+page.svelte."""

from __future__ import annotations

import httpx
import rio

from src.config.backend import API_BASE_URL
from src.modules.base.stores import auth as auth_store
from src.modules.base.utils import auth_api


@rio.page(
    name="Home",
    url_segment="",
)
class HomePage(rio.Component):
    health: str = "…"
    sample: str = "…"
    api_error: str = ""
    me_check: str = "not tested"
    me_loading: bool = False
    _probed: bool = False

    @rio.event.on_populate
    async def _probe_api(self) -> None:
        if self._probed:
            return
        self._probed = True
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                health_res = await client.get(f"{API_BASE_URL}/utils/health-check")
                if health_res.is_success:
                    self.health = str(health_res.json())
                else:
                    self.health = f"HTTP {health_res.status_code}"

                sample_res = await client.get(f"{API_BASE_URL}/sample")
                if sample_res.is_success:
                    body = sample_res.json()
                    self.sample = body.get("message", "ok")
                else:
                    self.sample = f"HTTP {sample_res.status_code}"
        except Exception as exc:
            self.api_error = str(exc) or "Request failed"
            self.health = "ERR"

    async def _test_me(self) -> None:
        token = auth_store.get_token(self.session)
        if not token:
            self.me_check = "no token in store"
            return
        self.me_loading = True
        self.force_refresh()
        try:
            user = await auth_api.fetch_current_user(token)
            suffix = " (superuser)" if user.is_superuser else ""
            self.me_check = f"{user.email}{suffix}"
        except Exception as exc:
            self.me_check = str(exc) or "request failed"
        finally:
            self.me_loading = False

    def build(self) -> rio.Component:
        health_status = self.api_error or self.health
        return rio.Column(
            rio.Text("Dashboard", style="heading1"),
            rio.Text(
                "API health checks and session verification. Default superuser: admin@example.com",
                style="dim",
            ),
            rio.Row(
                rio.Card(
                    rio.Column(
                        rio.Text("Authenticated /me", style="heading3"),
                        rio.Button(
                            "Calling /me…" if self.me_loading else "Test GET /base/login/me",
                            on_press=self._test_me,
                            is_loading=self.me_loading,
                            color="primary",
                        ),
                        rio.Text(self.me_check, style="dim"),
                        spacing=0.8,
                        margin=1.5,
                    ),
                    grow_x=True,
                ),
                rio.Card(
                    rio.Column(
                        rio.Text("Health check", style="heading3"),
                        rio.Text("GET /api/v1/utils/health-check", style="dim"),
                        rio.Text(health_status),
                        spacing=0.6,
                        margin=1.5,
                    ),
                    grow_x=True,
                ),
                spacing=1.5,
            ),
            rio.Card(
                rio.Column(
                    rio.Text("Sample module", style="heading3"),
                    rio.Text("GET /api/v1/sample", style="dim"),
                    rio.Text(self.sample),
                    spacing=0.6,
                    margin=1.5,
                ),
            ),
            spacing=1.5,
            align_y=0,
        )
