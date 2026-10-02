"""Switch with a text label (Switch has no `text` prop in rio-ui)."""

from __future__ import annotations

import rio


class LabeledSwitch(rio.Component):
    """Two-way bound switch with a text label."""

    is_on: bool = False
    label: str = ""

    def build(self) -> rio.Component:
        return rio.Row(
            rio.Switch(is_on=self.bind().is_on),
            rio.Text(self.label),
            spacing=0.5,
            align_y=0.5,
        )
