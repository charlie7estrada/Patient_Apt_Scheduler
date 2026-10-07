import pytest

from app.models import ChatMessageLog, User, UserRole
from app.services.auth import create_access_token, hash_password
from app.services.chat import ChatUnavailableError
from app.services.rate_limit import CHAT_LIMIT_MESSAGE, GUEST_CHAT_LIMIT


@pytest.fixture()
def guest(db_session):
    guest = User(
        email="guest-test@guest.patientscheduler.app",
        hashed_password=hash_password("not-used-for-login"),
        full_name="Demo Guest",
        role=UserRole.patient,
        is_guest=True,
    )
    db_session.add(guest)
    db_session.commit()
    db_session.refresh(guest)
    return guest


# Replaces the Mistral call so tests control the outcome and can count how often it ran
def _stub_chat(monkeypatch, reply="ok", error=None):
    calls = []

    def fake_chat_response(text, history, patient, db):
        calls.append(text)
        if error:
            raise error
        return reply

    monkeypatch.setattr("app.routes.chat.get_chat_response", fake_chat_response)
    return calls


def _send(client, user):
    token = create_access_token({"sub": user.email, "role": user.role.value})
    return client.post(
        "/api/v1/chat/",
        json={"text": "hi", "history": []},
        headers={"Authorization": f"Bearer {token}"},
    )


def _logged_messages(user, db):
    return db.query(ChatMessageLog).filter(ChatMessageLog.user_id == user.id).count()


def test_message_over_limit_gets_429_without_calling_model(client, guest, monkeypatch):
    calls = _stub_chat(monkeypatch)
    for _ in range(GUEST_CHAT_LIMIT):
        assert _send(client, guest).status_code == 200

    response = _send(client, guest)

    assert response.status_code == 429
    assert response.json()["detail"] == CHAT_LIMIT_MESSAGE
    assert response.headers["Retry-After"] == "3600"
    assert len(calls) == GUEST_CHAT_LIMIT


def test_successful_message_keeps_its_slot(client, db_session, patient, monkeypatch):
    _stub_chat(monkeypatch, reply="Booked!")

    response = _send(client, patient)

    assert response.status_code == 200
    assert response.json() == {"response": "Booked!"}
    assert _logged_messages(patient, db_session) == 1


def test_unavailable_model_refunds_the_slot(client, db_session, patient, monkeypatch):
    _stub_chat(monkeypatch, error=ChatUnavailableError("Try again shortly."))

    response = _send(client, patient)

    assert response.status_code == 503
    assert response.json()["detail"] == "Try again shortly."
    assert _logged_messages(patient, db_session) == 0


def test_unexpected_error_refunds_the_slot(client, db_session, patient, monkeypatch):
    _stub_chat(monkeypatch, error=RuntimeError("boom"))

    response = _send(client, patient)

    assert response.status_code == 500
    assert _logged_messages(patient, db_session) == 0
