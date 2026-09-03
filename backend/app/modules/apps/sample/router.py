import uuid

from fastapi import APIRouter, Response

from app.api.deps import CurrentUser, SessionDep
from app.modules.apps.sample import service
from app.modules.apps.sample.schemas import NoteCreate, NotePublic, NoteUpdate
from app.modules.base.schemas import Message

sample_router = APIRouter(prefix="/sample", tags=["[APPS] Sample"])


@sample_router.get("", response_model=Message)
def sample_root() -> Message:
    return Message(
        message="Sample module — see /sample/notes for the canonical CRUD example"
    )


@sample_router.get("/notes", response_model=list[NotePublic])
def list_notes(session: SessionDep, current_user: CurrentUser) -> list[NotePublic]:
    return service.list_notes(session, current_user)


@sample_router.post("/notes", response_model=NotePublic, status_code=201)
def create_note(
    session: SessionDep, current_user: CurrentUser, body: NoteCreate
) -> NotePublic:
    return service.create_note(session, current_user, body)


@sample_router.get("/notes/{note_id}", response_model=NotePublic)
def read_note(
    session: SessionDep, current_user: CurrentUser, note_id: uuid.UUID
) -> NotePublic:
    return service.get_note(session, current_user, note_id)


@sample_router.patch("/notes/{note_id}", response_model=NotePublic)
def update_note(
    session: SessionDep,
    current_user: CurrentUser,
    note_id: uuid.UUID,
    body: NoteUpdate,
) -> NotePublic:
    return service.update_note(session, current_user, note_id, body)


@sample_router.delete("/notes/{note_id}", status_code=204)
def delete_note(
    session: SessionDep, current_user: CurrentUser, note_id: uuid.UUID
) -> Response:
    service.delete_note(session, current_user, note_id)
    return Response(status_code=204)
