import asyncio


def test_ping_task():
    from app.worker.tasks import ping

    result = asyncio.run(ping({}, message="hello"))
    assert result == {"message": "hello", "status": "ok"}


def test_private_ping_job_requires_redis(client):
    response = client.post("/api/v1/private/jobs/ping/", params={"message": "test"})
    # Without Redis running, expect 503; with Redis+worker, 200.
    assert response.status_code in (200, 503)
