"""Canonical sample module UI — notes CRUD."""

from __future__ import annotations

import rio

from src.modules.apps.sample import api as notes_api
from src.modules.base.stores import auth as auth_store
from src.modules.base.utils.api_error import ApiError


@rio.page(
    name="Sample Notes",
    url_segment="sample/notes",
)
class SampleNotesPage(rio.Component):
    notes: list[notes_api.Note] = []
    title_input: str = ""
    content_input: str = ""
    editing_note_id: str | None = None
    edit_title_input: str = ""
    edit_content_input: str = ""
    status: str = ""
    loading: bool = False
    saving: bool = False

    def _token(self) -> str | None:
        return auth_store.get_token(self.session)

    def _handle_unauthorized(self) -> None:
        auth_store.apply_logout(self.session)
        self.session.navigate_to("/login")

    async def _load_notes(self) -> None:
        if auth_store.is_loading(self.session):
            return

        token = self._token()
        if not token:
            self.status = "Sign in to manage notes"
            self.notes = []
            return
        self.loading = True
        self.force_refresh()
        try:
            self.notes = await notes_api.list_notes(token)
            self.status = f"{len(self.notes)} note(s)"
        except ApiError as exc:
            if exc.status == 401:
                self._handle_unauthorized()
                return
            self.status = str(exc) or "Failed to load notes"
            self.notes = []
        except Exception as exc:
            self.status = str(exc) or "Failed to load notes"
            self.notes = []
        finally:
            self.loading = False

    @rio.event.on_populate
    async def _on_populate(self) -> None:
        await self._load_notes()

    def _close_edit(self) -> None:
        self.editing_note_id = None
        self.edit_title_input = ""
        self.edit_content_input = ""

    def _open_edit(self, note: notes_api.Note) -> None:
        self.editing_note_id = note.id
        self.edit_title_input = note.title
        self.edit_content_input = note.content

    async def _create(self) -> None:
        token = self._token()
        if not token:
            return
        title = self.title_input.strip()
        if not title:
            self.status = "Title is required"
            return
        self.saving = True
        self.force_refresh()
        try:
            await notes_api.create_note(token, title, self.content_input.strip())
            self.title_input = ""
            self.content_input = ""
            self.status = "Note created"
            await self._load_notes()
        except ApiError as exc:
            if exc.status == 401:
                self._handle_unauthorized()
                return
            self.status = str(exc) or "Create failed"
        except Exception as exc:
            self.status = str(exc) or "Create failed"
        finally:
            self.saving = False

    async def _save_edit(self) -> None:
        token = self._token()
        if not token or not self.editing_note_id:
            return
        title = self.edit_title_input.strip()
        if not title:
            self.status = "Title is required"
            return
        self.saving = True
        self.force_refresh()
        try:
            await notes_api.update_note(
                token,
                self.editing_note_id,
                title=title,
                content=self.edit_content_input.strip(),
            )
            self._close_edit()
            self.status = "Note updated"
            await self._load_notes()
        except ApiError as exc:
            if exc.status == 401:
                self._handle_unauthorized()
                return
            self.status = str(exc) or "Update failed"
        except Exception as exc:
            self.status = str(exc) or "Update failed"
        finally:
            self.saving = False

    async def _delete(self, note_id: str) -> None:
        token = self._token()
        if not token:
            return
        self.saving = True
        self.force_refresh()
        try:
            await notes_api.delete_note(token, note_id)
            if self.editing_note_id == note_id:
                self._close_edit()
            self.status = "Note deleted"
            await self._load_notes()
        except ApiError as exc:
            if exc.status == 401:
                self._handle_unauthorized()
                return
            self.status = str(exc) or "Delete failed"
        except Exception as exc:
            self.status = str(exc) or "Delete failed"
        finally:
            self.saving = False

    def _notes_table(self) -> rio.Component:
        if self.loading:
            return rio.Text("Loading notes…")
        if not self.notes:
            return rio.Text("No notes yet.", style="dim")

        rows: list[rio.Component] = [
            rio.Row(
                rio.Text("Title", style="heading3", grow_x=True),
                rio.Text("Content", style="heading3", grow_x=True),
                rio.Text("", min_width=6),
                spacing=1,
            )
        ]
        for note in self.notes:
            rows.append(
                rio.Row(
                    rio.Button(
                        note.title,
                        on_press=lambda n=note: self._open_edit(n),
                        style="plain-text",
                        color="primary",
                        grow_x=True,
                        align_x=0,
                    ),
                    rio.Text(note.content or "—", style="dim", grow_x=True),
                    rio.Button(
                        "Delete",
                        on_press=lambda n=note: self._delete(n.id),
                        color="danger",
                        is_loading=self.saving,
                    ),
                    spacing=1,
                    align_y=0.5,
                )
            )
        return rio.Column(*rows, spacing=0.8)

    def _edit_panel(self) -> rio.Component | None:
        if not self.editing_note_id:
            return None
        return rio.Card(
            rio.Column(
                rio.Row(
                    rio.Text("Edit note", style="heading3", grow_x=True),
                    rio.Button("Close", on_press=self._close_edit, style="plain-text"),
                    spacing=1,
                ),
                rio.Text("Update the title and content, then save.", style="dim"),
                rio.TextInput(text=self.bind().edit_title_input, label="Title"),
                rio.TextInput(text=self.bind().edit_content_input, label="Content"),
                rio.Row(
                    rio.Spacer(),
                    rio.Button(
                        "Delete",
                        on_press=lambda: self._delete(self.editing_note_id or ""),
                        color="danger",
                        is_loading=self.saving,
                    ),
                    rio.Button(
                        "Save changes",
                        on_press=self._save_edit,
                        color="primary",
                        is_loading=self.saving,
                    ),
                    spacing=1,
                ),
                spacing=1,
                margin=1.5,
            ),
            min_width=16,
        )

    def build(self) -> rio.Component:
        edit_panel = self._edit_panel()
        columns: list[rio.Component] = [
            rio.Card(
                rio.Column(
                    rio.Text("New note", style="heading3"),
                    rio.TextInput(text=self.bind().title_input, label="Title"),
                    rio.TextInput(text=self.bind().content_input, label="Content"),
                    rio.Button(
                        "Create note",
                        on_press=self._create,
                        is_loading=self.saving,
                        color="primary",
                    ),
                    spacing=1,
                    margin=1.5,
                ),
                min_width=16,
            ),
            rio.Card(
                rio.Column(
                    rio.Text("Your notes", style="heading3"),
                    rio.Text(self.status, style="dim"),
                    self._notes_table(),
                    spacing=1,
                    margin=1.5,
                ),
                grow_x=True,
            ),
        ]
        if edit_panel is not None:
            columns.append(edit_panel)

        proportions = [1, 2, 1] if edit_panel is not None else [1, 2]

        return rio.Column(
            rio.Text("Sample Notes", style="heading1"),
            rio.Text("Canonical CRUD module — Router → Service → Repository", style="dim"),
            rio.Row(
                *columns,
                spacing=1.5,
                proportions=proportions,
            ),
            spacing=1.5,
            align_y=0,
        )
