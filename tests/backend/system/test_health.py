def test_health_check(client):
    response = client.get("/api/v1/utils/health-check")
    assert response.status_code == 200
    assert response.json() is True


def test_sample_app(client):
    response = client.get("/api/v1/sample")
    assert response.status_code == 200
    assert "message" in response.json()


def test_private_signup_duplicate_email_returns_400(client):
    payload = {"email": "dup-signup@example.com", "password": "password123"}
    assert client.post("/api/v1/private/users", json=payload).status_code == 200
    response = client.post("/api/v1/private/users", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
