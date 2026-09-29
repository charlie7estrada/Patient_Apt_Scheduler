from urllib.parse import parse_qs, urlparse

import pytest

from app.models import User


@pytest.fixture()
def sent_links(monkeypatch):
    sent = []
    monkeypatch.setattr(
        "app.routes.auth.send_password_reset_email",
        lambda to, link: sent.append((to, link)),
    )
    return sent


def _token_from(link):
    return parse_qs(urlparse(link).query)["token"][0]


def test_forgot_password_response_is_same_for_unknown_email(client, patient, sent_links):
    known = client.post("/api/v1/auth/forgot-password", json={"email": patient.email})
    unknown = client.post("/api/v1/auth/forgot-password", json={"email": "ghost@example.com"})

    assert unknown.status_code == known.status_code == 202
    assert unknown.json() == known.json()
    assert [to for to, _ in sent_links] == [patient.email]


def test_forgot_password_skips_guests(client, db_session, sent_links):
    client.post("/api/v1/auth/guest")
    guest = db_session.query(User).filter(User.is_guest.is_(True)).one()

    client.post("/api/v1/auth/forgot-password", json={"email": guest.email})

    assert sent_links == []


def test_reset_password_lets_user_log_in_with_new_password(client, patient, sent_links):
    client.post("/api/v1/auth/forgot-password", json={"email": patient.email})
    token = _token_from(sent_links[0][1])

    response = client.post("/api/v1/auth/reset-password", json={
        "token": token,
        "new_password": "brandnewpass456",
    })
    login = client.post("/api/v1/auth/login", json={
        "email": patient.email,
        "password": "brandnewpass456",
    })

    assert response.status_code == 200
    assert login.status_code == 200


def test_reset_password_rejects_invalid_token(client):
    response = client.post("/api/v1/auth/reset-password", json={
        "token": "not-a-real-token",
        "new_password": "brandnewpass456",
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "This reset link is invalid or has expired"
