from __future__ import annotations

from pathlib import Path

import rio

from .modules.base import APP_NAME
from .modules.base.root_component import RootComponent
from .modules.base.stores.auth import AuthSettings, AuthUser, apply_login, apply_logout, set_loading
from .modules.base.stores.theme import (
    DARK_THEME,
    LIGHT_THEME,
    ThemeSettings,
    apply_theme,
    migrate_theme_settings,
)
from .modules.base.utils import auth_api


async def on_session_start(session: rio.Session) -> None:
    """Validate persisted token against GET /base/login/me."""
    migrate_theme_settings(session)
    set_loading(session, True)
    settings = session[AuthSettings]
    token = settings.auth_token
    if not token or not settings.user_email:
        set_loading(session, False)
        apply_theme(session)
        return

    try:
        user = await auth_api.fetch_current_user(token)
        apply_login(session, token, user)
    except Exception:
        apply_logout(session)
    finally:
        set_loading(session, False)

    apply_theme(session)


app = rio.App(
    name=APP_NAME,
    build=RootComponent,
    theme=(LIGHT_THEME, DARK_THEME),
    icon=Path(__file__).parent / "assets" / "pwa-192.png",
    default_attachments=[AuthSettings(), ThemeSettings()],
    on_session_start=on_session_start,
    assets_dir=Path(__file__).parent / "assets",
)
