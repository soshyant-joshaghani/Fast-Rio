import uuid

from sqlmodel import Session, delete, select

from app.modules.apps.sample.models import Note, utc_now
from app.modules.apps.sample.schemas import NoteCreate, NoteUpdate


def create_note(*, session: Session, owner_id: uuid.UUID, data: NoteCreate) -> Note:
    note = Note.model_validate(data, update={"owner_id": owner_id})
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


def list_notes_by_owner(*, session: Session, owner_id: uuid.UUID) -> list[Note]:
    statement = (
        select(Note)
        .where(Note.owner_id == owner_id)
        .order_by(Note.updated_at.desc())  # type: ignore[attr-defined]
    )
    return list(session.exec(statement).all())


def get_note_by_id(*, session: Session, note_id: uuid.UUID) -> Note | None:
    return session.get(Note, note_id)


def update_note(*, session: Session, note: Note, data: NoteUpdate) -> Note:
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        note.sqlmodel_update(update_data)
        note.updated_at = utc_now()
        session.add(note)
        session.commit()
        session.refresh(note)
    return note


def delete_note(*, session: Session, note: Note) -> None:
    session.delete(note)
    session.commit()


def delete_notes_by_owner(*, session: Session, owner_id: uuid.UUID) -> None:
    statement = delete(Note).where(Note.owner_id == owner_id)
    session.exec(statement)  # type: ignore[call-overload]
