from datetime import datetime, timedelta

from app.models import Appointment, AppointmentStatus, User, UserRole
from app.services.appointments import CLINIC_TZ
from app.services.auth import create_access_token, hash_password
from app.services.chat import _execute_update_appointment


def _headers(user):
    token = create_access_token({"sub": user.email, "role": user.role.value})
    return {"Authorization": f"Bearer {token}"}


def _appointment(db_session, patient, provider, status):
    appointment = Appointment(
        patient_id=patient.id,
        provider_id=provider.id,
        scheduled_at=datetime.now(CLINIC_TZ) + timedelta(days=2),
        reason="Checkup",
        status=status,
    )
    db_session.add(appointment)
    db_session.commit()
    db_session.refresh(appointment)
    return appointment


def test_archiving_hides_appointment_from_default_list(client, db_session, patient, provider):
    appointment = _appointment(db_session, patient, provider, AppointmentStatus.cancelled)

    response = client.post(f"/api/v1/appointments/{appointment.id}/archive", headers=_headers(patient))
    assert response.status_code == 204

    listed = client.get("/api/v1/appointments/", headers=_headers(patient)).json()
    assert listed == []


def test_archived_appointment_is_returned_when_requested(client, db_session, patient, provider):
    appointment = _appointment(db_session, patient, provider, AppointmentStatus.completed)
    client.post(f"/api/v1/appointments/{appointment.id}/archive", headers=_headers(patient))

    listed = client.get(
        "/api/v1/appointments/?include_archived=true", headers=_headers(patient)
    ).json()

    assert [a["id"] for a in listed] == [appointment.id]
    assert listed[0]["is_archived"] is True


def test_archiving_does_not_delete_the_row(client, db_session, patient, provider):
    appointment = _appointment(db_session, patient, provider, AppointmentStatus.cancelled)
    client.post(f"/api/v1/appointments/{appointment.id}/archive", headers=_headers(patient))

    db_session.refresh(appointment)
    assert appointment.is_archived is True
    assert appointment.status == AppointmentStatus.cancelled


def test_cannot_archive_an_active_appointment(client, db_session, patient, provider):
    appointment = _appointment(db_session, patient, provider, AppointmentStatus.confirmed)

    response = client.post(f"/api/v1/appointments/{appointment.id}/archive", headers=_headers(patient))

    assert response.status_code == 400
    db_session.refresh(appointment)
    assert appointment.is_archived is False


def test_cannot_archive_another_patients_appointment(client, db_session, patient, provider):
    other = User(
        email="other@example.com",
        hashed_password=hash_password("securepassword123"),
        full_name="Other Patient",
        role=UserRole.patient,
    )
    db_session.add(other)
    db_session.commit()

    appointment = _appointment(db_session, patient, provider, AppointmentStatus.cancelled)

    response = client.post(f"/api/v1/appointments/{appointment.id}/archive", headers=_headers(other))

    assert response.status_code == 404
    db_session.refresh(appointment)
    assert appointment.is_archived is False


def test_rescheduling_an_archived_appointment_unarchives_it(db_session, patient, provider):
    appointment = _appointment(db_session, patient, provider, AppointmentStatus.completed)
    appointment.is_archived = True
    db_session.commit()

    later = datetime.now(CLINIC_TZ) + timedelta(days=9)
    while later.weekday() >= 5:
        later += timedelta(days=1)

    result = _execute_update_appointment(
        {
            "appointment_id": appointment.id,
            "date": later.strftime("%Y-%m-%d"),
            "time": "10:00",
            "reason": "Rebooked",
        },
        patient,
        db_session,
    )

    assert result["status"] == "confirmed"
    db_session.refresh(appointment)
    assert appointment.is_archived is False
