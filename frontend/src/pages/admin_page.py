"""SuperAdmin user management."""

from __future__ import annotations

import rio

from src.modules.base.ui.labeled_switch import LabeledSwitch
from src.modules.base.users import api as users_api
from src.modules.base.stores import auth as auth_store
from src.modules.base.stores.auth import AuthUser


@rio.page(
    name="Admin",
    url_segment="admin",
)
class AdminPage(rio.Component):
    users: list[users_api.User] = []
    selected_id: str | None = None
    email_input: str = ""
    full_name_input: str = ""
    password_input: str = ""
    is_active: bool = False
    is_superuser: bool = False
    status: str = ""
    loading: bool = False
    saving: bool = False

    def _token(self) -> str | None:
        return auth_store.get_token(self.session)

    def _current_user(self) -> AuthUser | None:
        if not auth_store.is_authenticated(self.session):
            return None
        try:
            return self.session[AuthUser]
        except KeyError:
            return auth_store.settings_to_user(self.session[auth_store.AuthSettings])

    async def _load_users(self) -> None:
        token = self._token()
        if not token:
            return
        self.loading = True
        try:
            self.users = await users_api.list_users(token)
            self.status = f"{len(self.users)} user(s)"
        except Exception as exc:
            self.status = str(exc) or "Failed to load users"
            self.users = []
        finally:
            self.loading = False

    @rio.event.on_populate
    async def _on_populate(self) -> None:
        user = self._current_user()
        if user and user.is_superuser:
            await self._load_users()

    def _select_user(self, user: users_api.User) -> None:
        self.selected_id = user.id
        self.email_input = user.email
        self.full_name_input = user.full_name or ""
        self.password_input = ""
        self.is_active = user.is_active
        self.is_superuser = user.is_superuser
        self.status = f"Editing: {user.email}"

    def _clear_form(self) -> None:
        self.selected_id = None
        self.email_input = ""
        self.full_name_input = ""
        self.password_input = ""
        self.is_active = False
        self.is_superuser = False
        self.status = "New user"

    async def _save(self, _event: rio.TextInputConfirmEvent | None = None) -> None:
        token = self._token()
        if not token:
            self.status = "Sign in first"
            return
        email = self.email_input.strip()
        if not email:
            self.status = "Email is required"
            return
        self.saving = True
        try:
            if self.selected_id:
                await users_api.update_user(
                    token,
                    self.selected_id,
                    email=email,
                    full_name=self.full_name_input.strip() or None,
                    password=self.password_input or None,
                    is_active=self.is_active,
                    is_superuser=self.is_superuser,
                )
                self.status = "User updated"
            else:
                if len(self.password_input) < 8:
                    self.status = "Password must be at least 8 characters"
                    self.saving = False
                    return
                await users_api.create_user(
                    token,
                    email=email,
                    password=self.password_input,
                    full_name=self.full_name_input.strip() or None,
                    is_active=self.is_active,
                    is_superuser=self.is_superuser,
                )
                self.status = "User created"
            self._clear_form()
            await self._load_users()
        except Exception as exc:
            self.status = str(exc) or "Save failed"
        finally:
            self.saving = False

    async def _delete_selected(self) -> None:
        token = self._token()
        if not token or not self.selected_id:
            return
        current = self._current_user()
        if current and current.id == self.selected_id:
            self.status = "Cannot delete your own account here"
            return
        self.saving = True
        try:
            await users_api.delete_user(token, self.selected_id)
            self.status = "User deleted"
            self._clear_form()
            await self._load_users()
        except Exception as exc:
            self.status = str(exc) or "Delete failed"
        finally:
            self.saving = False

    def _users_list(self) -> rio.Component:
        if self.loading:
            return rio.Text("Loading users…")
        if not self.users:
            return rio.Text("No users yet", style="dim")
        rows: list[rio.Component] = []
        for user in self.users:
            label = user.email
            if user.is_superuser:
                label += " (superuser)"
            is_selected = user.id == self.selected_id
            rows.append(
                rio.Button(
                    label,
                    on_press=lambda u=user: self._select_user(u),
                    color="primary" if is_selected else "neutral",
                    grow_x=True,
                )
            )
        return rio.Column(*rows, spacing=0.5)

    def build(self) -> rio.Component:
        user = self._current_user()
        if user is None:
            return rio.Banner(text="Sign in to manage users", style="warning")
        if not user.is_superuser:
            return rio.Banner(
                text="Superuser access required. You do not have permission to view this page.",
                style="danger",
            )

        return rio.Column(
            rio.Row(
                rio.Column(
                    rio.Text("Users", style="heading1"),
                    rio.Text("Manage user accounts and permissions", style="dim"),
                    spacing=0.4,
                ),
                rio.Spacer(),
                rio.Button("Add user", on_press=self._clear_form, color="secondary"),
                align_y=0.5,
            ),
            rio.Row(
                rio.Card(
                    rio.Column(
                        rio.Text("All users", style="heading3"),
                        self._users_list(),
                        rio.Text(self.status, style="dim"),
                        spacing=1,
                        margin=1.5,
                        grow_x=True,
                    ),
                    grow_x=True,
                ),
                rio.Card(
                    rio.Column(
                        rio.Text(
                            "Edit user" if self.selected_id else "New user",
                            style="heading3",
                        ),
                        rio.TextInput(
                            text=self.bind().email_input,
                            label="Email",
                            on_confirm=self._save,
                        ),
                        rio.TextInput(
                            text=self.bind().full_name_input,
                            label="Full name",
                            on_confirm=self._save,
                        ),
                        rio.TextInput(
                            text=self.bind().password_input,
                            label="Password (required for new user)",
                            is_secret=True,
                            on_confirm=self._save,
                        ),
                        LabeledSwitch(is_on=self.bind().is_active, label="Is active"),
                        LabeledSwitch(is_on=self.bind().is_superuser, label="Is superuser"),
                        rio.Row(
                            rio.Button(
                                "Save",
                                on_press=self._save,
                                is_loading=self.saving,
                                color="primary",
                            ),
                            rio.Button(
                                "Delete",
                                on_press=self._delete_selected,
                                is_loading=self.saving,
                                color="danger",
                                is_sensitive=self.selected_id is not None,
                            ),
                            spacing=0.8,
                        ),
                        spacing=1,
                        margin=1.5,
                        grow_x=True,
                    ),
                    grow_x=True,
                ),
                spacing=1.5,
            ),
            spacing=1.5,
            align_y=0,
        )
