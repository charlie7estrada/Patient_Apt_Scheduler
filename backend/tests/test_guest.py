from datetime import datetime, timedelta, timezone

from app.models import Appointment, AppointmentStatus, User, UserRole
from app.services.chat import CLINIC_TZ, _validate_scheduled_at
from app.services.guest import (
    GUEST_EMAIL_DOMAIN,
    SAMPLE_REASONS,
    create_guest_user,
    purge_expired_guests,
)


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

def _appointments_for(db_session, user):
    return db_session.query(Appointment).filter(Appointment.patient_id == user.id).all()


def test_guest_gets_two_sample_appointments(client, db_session, provider):
    client.post("/api/v1/auth/guest")

    guest = _guest_users(db_session).one()
    appointments = _appointments_for(db_session, guest)

    assert len(appointments) == 2
    assert {a.reason for a in appointments} == set(SAMPLE_REASONS)
    assert all(a.provider_id == provider.id for a in appointments)
    assert all(a.status == AppointmentStatus.pending for a in appointments)


def test_sample_appointments_are_bookable_slots_on_different_days(client, db_session, provider):
    client.post("/api/v1/auth/guest")

    guest = _guest_users(db_session).one()
    slots = [a.scheduled_at.replace(tzinfo=CLINIC_TZ) for a in _appointments_for(db_session, guest)]

    assert all(_validate_scheduled_at(slot) is None for slot in slots)
    assert len({slot.date() for slot in slots}) == 2


def test_sample_appointments_do_not_double_book_provider(client, db_session, provider):
    for _ in range(3):
        client.post("/api/v1/auth/guest")

    scheduled = [a.scheduled_at for a in db_session.query(Appointment).all()]

    assert len(scheduled) == 6
    assert len(set(scheduled)) == 6


def test_guest_sees_sample_appointments_through_api(client, provider):
    token = client.post("/api/v1/auth/guest").json()["access_token"]

    response = client.get(
        "/api/v1/appointments/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()) == 2


def _age(db_session, user, hours):
    user.created_at = datetime.now(timezone.utc) - timedelta(hours=hours)
    db_session.commit()


def test_purge_deletes_expired_guests_and_their_appointments(db_session, provider):
    guest = create_guest_user(db_session)
    guest_id = guest.id
    _age(db_session, guest, hours=25)

    purged = purge_expired_guests(db_session)

    assert purged == 1
    assert db_session.get(User, guest_id) is None
    assert db_session.query(Appointment).filter(Appointment.patient_id == guest_id).count() == 0


def test_purge_keeps_recent_guests(db_session, provider):
    guest = create_guest_user(db_session)
    _age(db_session, guest, hours=23)

    assert purge_expired_guests(db_session) == 0
    assert len(_appointments_for(db_session, guest)) == 2


def test_purge_keeps_registered_users(db_session, patient):
    _age(db_session, patient, hours=24 * 30)

    assert purge_expired_guests(db_session) == 0
    assert db_session.get(User, patient.id) is not None
