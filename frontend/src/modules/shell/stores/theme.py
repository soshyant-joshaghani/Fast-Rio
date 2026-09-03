"""Theme preference persisted in UserSettings."""

from __future__ import annotations

import rio

LIGHT_THEME = rio.Theme.from_colors(
    primary_color=rio.Color.from_hex("0ea5e9"),
    secondary_color=rio.Color.from_hex("8b5cf6"),
    background_color=rio.Color.from_hex("fafafa"),
    neutral_color=rio.Color.from_hex("ffffff"),
    mode="light",
)

DARK_THEME = rio.Theme.from_colors(
    primary_color=rio.Color.from_hex("0ea5e9"),
    secondary_color=rio.Color.from_hex("8b5cf6"),
    background_color=rio.Color.from_hex("09090b"),
    neutral_color=rio.Color.from_hex("18181b"),
    mode="dark",
)


class ThemeSettings(rio.UserSettings):
    mode: str = "system"  # "system" | "light" | "dark"
    prefs_version: int = 1


def migrate_theme_settings(session: rio.Session) -> None:
    """Upgrade persisted theme prefs from the old implicit-dark default."""
    settings = session[ThemeSettings]
    if settings.prefs_version >= 2:
        return
    if settings.mode != "light":
        settings.mode = "system"
    settings.prefs_version = 2
    session.attach(settings)


def _effective_is_light(session: rio.Session) -> bool:
    settings = session[ThemeSettings]
    if settings.mode == "light":
        return True
    if settings.mode == "dark":
        return False
    return session._prefers_light_theme


def is_dark(session: rio.Session) -> bool:
    return not _effective_is_light(session)


def apply_theme(session: rio.Session) -> None:
    session.theme = LIGHT_THEME if _effective_is_light(session) else DARK_THEME


def toggle_theme(session: rio.Session) -> None:
    settings = session[ThemeSettings]
    settings.mode = "light" if is_dark(session) else "dark"
    session.attach(settings)
    apply_theme(session)
