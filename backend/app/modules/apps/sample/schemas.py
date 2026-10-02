import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class NoteCreate(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(default="", max_length=10000)


class NoteUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None, max_length=10000)


class NotePublic(SQLModel):
    id: uuid.UUID
    title: str
    content: str
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
