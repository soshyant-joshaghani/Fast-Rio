import uuid

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.apps.sample import repository
from app.modules.apps.sample.models import Note
from app.modules.apps.sample.schemas import NoteCreate, NoteUpdate
from app.modules.base.users.models import User


def list_notes(session: Session, user: User) -> list[Note]:
    return repository.list_notes_by_owner(session=session, owner_id=user.id)  # type: ignore[arg-type]


def create_note(session: Session, user: User, data: NoteCreate) -> Note:
    title = data.title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="Title cannot be empty")
    payload = NoteCreate(title=title, content=data.content.strip())
    return repository.create_note(
        session=session,
        owner_id=user.id,  # type: ignore[arg-type]
        data=payload,
    )


def get_note(session: Session, user: User, note_id: uuid.UUID) -> Note:
    note = repository.get_note_by_id(session=session, note_id=note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to access this note")
    return note


def update_note(
    session: Session,
    user: User,
    note_id: uuid.UUID,
    data: NoteUpdate,
) -> Note:
    note = get_note(session, user, note_id)
    if data.title is not None and not data.title.strip():
        raise HTTPException(status_code=422, detail="Title cannot be empty")
    clean = NoteUpdate(
        title=data.title.strip() if data.title is not None else None,
        content=data.content.strip() if data.content is not None else None,
    )
    return repository.update_note(session=session, note=note, data=clean)


def delete_note(session: Session, user: User, note_id: uuid.UUID) -> None:
    note = get_note(session, user, note_id)
    repository.delete_note(session=session, note=note)
