import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, SuperAdminUser
from app.modules.apps.sample.repository import delete_notes_by_owner
from app.modules.base.schemas import Message
from app.modules.base.users import crud
from app.modules.base.users.models import User, UserCreate, UserPublic, UsersPublic, UserUpdate

users_router_admin = APIRouter(
    prefix="/users", tags=["[SUPERADMIN] Core - User Management"]
)


@users_router_admin.get("/admin", response_model=UsersPublic)
def read_users(
    session: SessionDep, current_user: SuperAdminUser, skip: int = 0, limit: int = 100
) -> Any:
    count = session.exec(select(func.count()).select_from(User)).one()
    statement = select(User).order_by(User.email).offset(skip).limit(limit)
    users = session.exec(statement).all()
    return UsersPublic(data=[UserPublic.model_validate(u) for u in users], count=count)


@users_router_admin.post("/admin", response_model=UserPublic)
def create_user(
    *, session: SessionDep, current_user: SuperAdminUser, user_in: UserCreate
) -> Any:
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    return crud.create_user(session=session, user_create=user_in)


@users_router_admin.get("/{user_id}/admin", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@users_router_admin.patch("/{user_id}/admin", response_model=UserPublic)
def update_user(
    *,
    session: SessionDep,
    super_admin: SuperAdminUser,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    return crud.update_user(session=session, db_user=db_user, user_in=user_in)


@users_router_admin.delete("/{user_id}/admin")
def delete_user(
    session: SessionDep,
    current_user: CurrentUser,
    super_admin: SuperAdminUser,
    user_id: uuid.UUID,
) -> Message:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    delete_notes_by_owner(session=session, owner_id=user_id)
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")
