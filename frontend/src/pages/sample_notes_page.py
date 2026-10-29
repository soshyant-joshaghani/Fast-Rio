"""Canonical sample module UI — notes CRUD (one form panel above, list below)."""

from __future__ import annotations

import typing as t

import rio

from src.modules.apps.sample import api as notes_api
from src.modules.base.http import ApiError
from src.modules.base.stores import auth as auth_store


@rio.page(
    name="Sample Notes",
    url_segment="sample/notes",
)
class SampleNotesPage(rio.Component):
    notes: list[notes_api.Note] = []
    title_input: str = ""
    content_input: str = ""
    editing_note_id: str | None = None  # None = creating a new note
    status: str = ""
    loading: bool = False
    saving: bool = False

    def _token(self) -> str | None:
        return auth_store.get_token(self.session)

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
                self._logout()
                return
            self.status = str(exc) or "Failed to load notes"
            self.notes = []
        except Exception as exc:
            self.status = str(exc) or "Failed to load notes"
            self.notes = []
        finally:
            self.loading = False

    def _logout(self) -> None:
        auth_store.apply_logout(self.session)
        self.session.navigate_to("/")

    async def _run(self, action: t.Callable[[str], t.Awaitable[None]], done: str, failed: str) -> bool:
        """Run a write call, then reload the list; shared error/401 handling. True on success."""
        token = self._token()
        if not token:
            return False
        self.saving = True
        self.force_refresh()
        try:
            await action(token)
            self.status = done
            await self._load_notes()
            return True
        except ApiError as exc:
            if exc.status == 401:
                self._logout()
                return False
            self.status = str(exc) or failed
        except Exception as exc:
            self.status = str(exc) or failed
        finally:
            self.saving = False
        return False

    @rio.event.on_populate
    async def _on_populate(self) -> None:
        await self._load_notes()

    def _reset_form(self) -> None:
        self.editing_note_id = None
        self.title_input = ""
        self.content_input = ""

    def _start_edit(self, note: notes_api.Note) -> None:
        self.editing_note_id = note.id
        self.title_input = note.title
        self.content_input = note.content

    async def _submit(self) -> None:
        title = self.title_input.strip()
        if not title:
            self.status = "Title is required"
            return
        content = self.content_input.strip()
        note_id = self.editing_note_id

        if note_id:
            ok = await self._run(
                lambda tok: notes_api.update_note(tok, note_id, title=title, content=content),
                "Note updated",
                "Update failed",
            )
        else:
            ok = await self._run(
                lambda tok: notes_api.create_note(tok, title, content),
                "Note created",
                "Create failed",
            )
        if ok:
            self._reset_form()

    async def _delete(self, note_id: str) -> None:
        ok = await self._run(lambda tok: notes_api.delete_note(tok, note_id), "Note deleted", "Delete failed")
        if ok and self.editing_note_id == note_id:
            self._reset_form()

    def _form_panel(self) -> rio.Component:
        editing = self.editing_note_id is not None
        buttons: list[rio.Component] = [
            rio.Button(
                "Save changes" if editing else "Add note",
                on_press=self._submit,
                color="primary",
                is_loading=self.saving,
            )
        ]
        if editing:
            buttons.append(rio.Button("Cancel", on_press=self._reset_form, style="minor"))

        return rio.Card(
            rio.Column(
                rio.Text("Edit note" if editing else "New note", style="heading3"),
                rio.TextInput(text=self.bind().title_input, label="Title"),
                rio.TextInput(text=self.bind().content_input, label="Content"),
                rio.Row(*buttons, rio.Spacer(), spacing=1),
                spacing=1,
                margin=1.5,
            ),
        )

    def _note_row(self, note: notes_api.Note) -> rio.Component:
        # Clicking the title/content area opens the note in the form above.
        return rio.Row(
            rio.PointerEventListener(
                rio.Rectangle(
                    content=rio.Row(
                        rio.Text(note.title, grow_x=True, overflow="ellipsize"),
                        rio.Text(note.content or "—", style="dim", grow_x=True, overflow="ellipsize"),
                        spacing=1,
                        margin=0.6,
                    ),
                    fill=rio.Color.TRANSPARENT,
                    cursor="pointer",
                    ripple=True,
                    corner_radius=0.5,
                ),
                on_press=lambda _e, n=note: self._start_edit(n),
                grow_x=True,
            ),
            rio.Button("Delete", on_press=lambda n=note: self._delete(n.id), color="danger"),
            spacing=1,
            align_y=0.5,
        )

    def _list_panel(self) -> rio.Component:
        if self.loading:
            body: rio.Component = rio.Text("Loading notes…")
        elif not self.notes:
            body = rio.Text("No notes yet.", style="dim")
        else:
            body = rio.Column(*(self._note_row(n) for n in self.notes), spacing=0.8)

        return rio.Card(
            rio.Column(
                rio.Row(
                    rio.Text("Your notes", style="heading3", grow_x=True),
                    rio.Text(self.status, style="dim"),
                    spacing=1,
                ),
                body,
                spacing=1,
                margin=1.5,
            ),
        )

    def build(self) -> rio.Component:
        return rio.Column(
            rio.Text("Sample Notes", style="heading1"),
            rio.Text("Canonical CRUD module — Router → Service → Repository", style="dim"),
            self._form_panel(),
            self._list_panel(),
            spacing=1.5,
            align_y=0,
        )
