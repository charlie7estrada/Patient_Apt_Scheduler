from app.models import User, UserRole
from app.services.guest import GUEST_EMAIL_DOMAIN


def _guest_users(db_session):
    return db_session.query(User).filter(User.is_guest.is_(True))


def test_guest_login_returns_token(client):
    response = client.post("/api/v1/auth/guest")

    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_guest_login_creates_guest_patient(client, db_session):
    client.post("/api/v1/auth/guest")

    guest = _guest_users(db_session).one()
    assert guest.role == UserRole.patient
    assert guest.email.endswith(f"@{GUEST_EMAIL_DOMAIN}")


def test_each_guest_login_creates_separate_account(client, db_session):
    client.post("/api/v1/auth/guest")
    client.post("/api/v1/auth/guest")

    assert _guest_users(db_session).count() == 2


def test_guest_token_authenticates(client):
    token = client.post("/api/v1/auth/guest").json()["access_token"]

    response = client.get(
        "/api/v1/appointments/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


def test_registered_users_are_not_guests(client, db_session):
    client.post("/api/v1/auth/register", json={
        "email": "patient@example.com",
        "password": "securepassword123",
        "full_name": "Test Patient",
        "role": "patient",
    })

    user = db_session.query(User).filter(User.email == "patient@example.com").one()
    assert user.is_guest is False
