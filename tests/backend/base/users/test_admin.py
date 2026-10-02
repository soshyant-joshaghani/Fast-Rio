import uuid

from app.core.config import settings
from app.modules.base.users import crud
from app.modules.base.users.models import UserCreate


def test_list_users_superuser(client, superuser_token_headers, db) -> None:
    username = f"user-{uuid.uuid4().hex[:8]}@example.com"
    crud.create_user(
        session=db,
        user_create=UserCreate(email=username, password="testpassword"),
    )

    response = client.get(
        f"{settings.API_V1_STR}/base/users/admin",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 2
    assert any(item["email"] == username for item in body["data"])


def test_create_user_superuser(client, superuser_token_headers, db) -> None:
    username = f"new-{uuid.uuid4().hex[:8]}@example.com"
    response = client.post(
        f"{settings.API_V1_STR}/base/users/admin",
        headers=superuser_token_headers,
        json={"email": username, "password": "testpassword"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == username
    assert crud.get_user_by_email(session=db, email=username) is not None


def test_create_user_forbidden_for_normal_user(client, db) -> None:
    username = f"normal-{uuid.uuid4().hex[:8]}@example.com"
    password = "testpassword"
    crud.create_user(
        session=db,
        user_create=UserCreate(email=username, password=password),
    )
    login = client.post(
        f"{settings.API_V1_STR}/base/login/access-token",
        data={"username": username, "password": password},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        f"{settings.API_V1_STR}/base/users/admin",
        headers=headers,
        json={"email": f"blocked-{uuid.uuid4().hex[:8]}@example.com", "password": password},
    )
    assert response.status_code == 403


def test_delete_self_forbidden(client, superuser_token_headers, db) -> None:
    superuser = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert superuser and superuser.id

    response = client.delete(
        f"{settings.API_V1_STR}/base/users/{superuser.id}/admin",
        headers=superuser_token_headers,
    )
    assert response.status_code == 403


def test_delete_user_with_notes(client, superuser_token_headers, db) -> None:
    from app.modules.apps.sample.repository import create_note
    from app.modules.apps.sample.schemas import NoteCreate

    username = f"notes-{uuid.uuid4().hex[:8]}@example.com"
    user = crud.create_user(
        session=db,
        user_create=UserCreate(email=username, password="testpassword"),
    )
    assert user.id
    create_note(
        session=db,
        owner_id=user.id,
        data=NoteCreate(title="Owned note", content="delete me with user"),
    )

    response = client.delete(
        f"{settings.API_V1_STR}/base/users/{user.id}/admin",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert crud.get_user_by_email(session=db, email=username) is None
