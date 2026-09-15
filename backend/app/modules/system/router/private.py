from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.core.arq import create_arq_pool
from app.core.security import get_password_hash
from app.modules.base.schemas import Message, PrivateUserCreate
from app.modules.base.users.models import User, UserPublic

private_router = APIRouter(tags=["[SYSTEM] System - Private"], prefix="/private")


@private_router.post("/users", response_model=UserPublic)
def create_user(user_in: PrivateUserCreate, session: SessionDep) -> Any:
    """Create a user (local dev only)."""
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@private_router.get("/ping", response_model=Message)
def private_ping() -> Message:
    return Message(message="private ok")


@private_router.post("/jobs/ping", response_model=dict[str, str])
async def enqueue_ping_job(message: str = "ping") -> dict[str, str]:
    """Enqueue the generic ping worker task (local dev — requires Redis + worker)."""
    try:
        pool = await create_arq_pool()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Redis unavailable: {exc}",
        ) from exc
    try:
        job = await pool.enqueue_job("ping", message)
    finally:
        await pool.aclose()
    if job is None:
        raise HTTPException(status_code=503, detail="Failed to enqueue job")
    return {"job_id": job.job_id, "message": message}
