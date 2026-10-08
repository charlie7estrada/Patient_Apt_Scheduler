from app.models import GuestCreationLog
from app.services.rate_limit import GUEST_CREATION_LIMIT, GUEST_CREATION_LIMIT_MESSAGE


def _start_demo(client, ip="203.0.113.7"):
    return client.post("/api/v1/auth/guest", headers={"True-Client-IP": ip})


def test_guest_creation_over_limit_gets_429(client):
    for _ in range(GUEST_CREATION_LIMIT):
        assert _start_demo(client).status_code == 201

    response = _start_demo(client)

    assert response.status_code == 429
    assert response.json()["detail"] == GUEST_CREATION_LIMIT_MESSAGE
    assert response.headers["Retry-After"] == "86400"


def test_guest_creation_limit_is_per_ip(client):
    for _ in range(GUEST_CREATION_LIMIT):
        _start_demo(client)

    assert _start_demo(client, ip="198.51.100.4").status_code == 201


def test_failed_guest_creation_refunds_the_slot(client, db_session, monkeypatch):
    def broken_create_guest_user(db):
        raise RuntimeError("boom")

    monkeypatch.setattr("app.routes.auth.create_guest_user", broken_create_guest_user)

    response = _start_demo(client)

    assert response.status_code == 500
    assert response.json()["detail"] == "Could not start the demo. Please try again."
    assert db_session.query(GuestCreationLog).count() == 0
