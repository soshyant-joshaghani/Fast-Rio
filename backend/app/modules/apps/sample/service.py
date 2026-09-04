"""Sample notes CRUD — canonical Redis read-cache showcase for Fast-* agents.

When Redis is reachable (full profile), list/get are cached; create/update/delete
invalidate. Slim / unreachable Redis soft-degrades to Postgres only.
"""

from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlmodel import Session

from app.core.cache import cache_delete, cache_delete_prefix, cache_get, cache_set
from app.modules.apps.sample import repository
from app.modules.apps.sample.models import Note
from app.modules.apps.sample.schemas import NoteCreate, NotePublic, NoteUpdate
from app.modules.base.users.models import User

_SAMPLE_PREFIX = "sample:notes:v1:"
_TTL_LIST = 120
_TTL_NOTE = 300


def _owner_token(user: User) -> str:
    return str(user.id)


def _list_key(user: User) -> str:
    return f"{_SAMPLE_PREFIX}list:{_owner_token(user)}"


def _note_key(user: User, note_id: uuid.UUID) -> str:
    return f"{_SAMPLE_PREFIX}note:{_owner_token(user)}:{note_id}"


def _invalidate_owner(user: User) -> None:
    cache_delete_prefix(f"{_SAMPLE_PREFIX}list:{_owner_token(user)}")
    cache_delete_prefix(f"{_SAMPLE_PREFIX}note:{_owner_token(user)}:")


def _to_public(note: Note) -> NotePublic:
    return NotePublic.model_validate(note)


def list_notes(session: Session, user: User) -> list[NotePublic]:
    key = _list_key(user)
    cached = cache_get(key)
    if isinstance(cached, list):
        return [NotePublic.model_validate(item) for item in cached]

    rows = repository.list_notes_by_owner(session=session, owner_id=user.id)  # type: ignore[arg-type]
    out = [_to_public(n) for n in rows]
    cache_set(key, [n.model_dump(mode="json") for n in out], _TTL_LIST)
    return out


def create_note(session: Session, user: User, data: NoteCreate) -> NotePublic:
    title = data.title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="Title cannot be empty")
    payload = NoteCreate(title=title, content=data.content.strip())
    note = repository.create_note(
        session=session,
        owner_id=user.id,  # type: ignore[arg-type]
        data=payload,
    )
    public = _to_public(note)
    _invalidate_owner(user)
    cache_set(
        _note_key(user, note.id),  # type: ignore[arg-type]
        public.model_dump(mode="json"),
        _TTL_NOTE,
    )
    return public


def get_note(session: Session, user: User, note_id: uuid.UUID) -> NotePublic:
    key = _note_key(user, note_id)
    cached = cache_get(key)
    if isinstance(cached, dict):
        public = NotePublic.model_validate(cached)
        if public.owner_id != user.id:
            raise HTTPException(status_code=403, detail="Not allowed to access this note")
        return public

    note = repository.get_note_by_id(session=session, note_id=note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to access this note")
    public = _to_public(note)
    cache_set(key, public.model_dump(mode="json"), _TTL_NOTE)
    return public


def update_note(
    session: Session,
    user: User,
    note_id: uuid.UUID,
    data: NoteUpdate,
) -> NotePublic:
    # Load from DB for mutation (bypass stale cache for write path).
    note = repository.get_note_by_id(session=session, note_id=note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to access this note")
    if data.title is not None and not data.title.strip():
        raise HTTPException(status_code=422, detail="Title cannot be empty")
    clean = NoteUpdate(
        title=data.title.strip() if data.title is not None else None,
        content=data.content.strip() if data.content is not None else None,
    )
    updated = repository.update_note(session=session, note=note, data=clean)
    public = _to_public(updated)
    _invalidate_owner(user)
    cache_set(_note_key(user, note_id), public.model_dump(mode="json"), _TTL_NOTE)
    return public


def delete_note(session: Session, user: User, note_id: uuid.UUID) -> None:
    note = repository.get_note_by_id(session=session, note_id=note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to access this note")
    repository.delete_note(session=session, note=note)
    cache_delete(_note_key(user, note_id))
    _invalidate_owner(user)
