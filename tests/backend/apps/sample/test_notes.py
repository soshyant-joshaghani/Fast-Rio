def test_list_notes_empty(client, superuser_token_headers):
    response = client.get(
        "/api/v1/sample/notes",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_list_note(client, superuser_token_headers):
    create = client.post(
        "/api/v1/sample/notes",
        headers=superuser_token_headers,
        json={"title": "Test note", "content": "Hello"},
    )
    assert create.status_code == 201
    body = create.json()
    assert body["title"] == "Test note"
    assert body["content"] == "Hello"
    note_id = body["id"]

    listing = client.get(
        "/api/v1/sample/notes",
        headers=superuser_token_headers,
    )
    assert listing.status_code == 200
    notes = listing.json()
    assert len(notes) == 1
    assert notes[0]["id"] == note_id


def test_update_note(client, superuser_token_headers):
    create = client.post(
        "/api/v1/sample/notes",
        headers=superuser_token_headers,
        json={"title": "Original", "content": "v1"},
    )
    note_id = create.json()["id"]

    update = client.patch(
        f"/api/v1/sample/notes/{note_id}",
        headers=superuser_token_headers,
        json={"title": "Updated", "content": "v2"},
    )
    assert update.status_code == 200
    body = update.json()
    assert body["title"] == "Updated"
    assert body["content"] == "v2"


def test_delete_note(client, superuser_token_headers):
    create = client.post(
        "/api/v1/sample/notes",
        headers=superuser_token_headers,
        json={"title": "Delete me", "content": ""},
    )
    note_id = create.json()["id"]

    delete = client.delete(
        f"/api/v1/sample/notes/{note_id}",
        headers=superuser_token_headers,
    )
    assert delete.status_code == 204

    read = client.get(
        f"/api/v1/sample/notes/{note_id}",
        headers=superuser_token_headers,
    )
    assert read.status_code == 404


def test_notes_require_auth(client):
    response = client.get("/api/v1/sample/notes")
    assert response.status_code == 401
