from datetime import datetime, timedelta

from app.models import Appointment, AppointmentStatus
from app.services.appointments import CLINIC_TZ, complete_past_appointments
from app.services.chat import _execute_cancel_appointment, build_system_prompt


def _appointment(db_session, patient, provider, minutes_from_now, status=AppointmentStatus.confirmed, reason="Checkup",):
    appointment = Appointment(
        patient_id=patient.id,
        provider_id=provider.id,
        scheduled_at=datetime.now(CLINIC_TZ) + timedelta(minutes=minutes_from_now),
        reason=reason,
        status=status,
    )
    db_session.add(appointment)
    db_session.commit()
    db_session.refresh(appointment)
    return appointment


def test_completes_appointment_past_its_slot(db_session, patient, provider):
    appointment = _appointment(db_session, patient, provider, minutes_from_now=-31)

    assert complete_past_appointments(db_session) == 1
    db_session.refresh(appointment)
    assert appointment.status == AppointmentStatus.completed


def test_keeps_appointment_still_in_its_slot(db_session, patient, provider):
    appointment = _appointment(db_session, patient, provider, minutes_from_now=-29)

    assert complete_past_appointments(db_session) == 0
    db_session.refresh(appointment)
    assert appointment.status == AppointmentStatus.confirmed


def test_keeps_upcoming_appointment(db_session, patient, provider):
    appointment = _appointment(db_session, patient, provider, minutes_from_now=60)

    assert complete_past_appointments(db_session) == 0
    db_session.refresh(appointment)
    assert appointment.status == AppointmentStatus.confirmed


def test_leaves_cancelled_appointments_cancelled(db_session, patient, provider):
    appointment = _appointment(
        db_session, patient, provider, minutes_from_now=-120, status=AppointmentStatus.cancelled
    )

    assert complete_past_appointments(db_session) == 0
    db_session.refresh(appointment)
    assert appointment.status == AppointmentStatus.cancelled


def test_completes_pending_appointments_too(db_session, patient, provider):
    appointment = _appointment(
        db_session, patient, provider, minutes_from_now=-120, status=AppointmentStatus.pending
    )

    assert complete_past_appointments(db_session) == 1
    db_session.refresh(appointment)
    assert appointment.status == AppointmentStatus.completed


def test_listing_appointments_completes_past_ones(client, db_session, patient, provider):
    _appointment(db_session, patient, provider, minutes_from_now=-45)
    token = client.post("/api/v1/auth/login", json={
        "email": patient.email,
        "password": "securepassword123",
    }).json()["access_token"]

    response = client.get(
        "/api/v1/appointments/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert [a["status"] for a in response.json()] == ["completed"]

def test_system_prompt_omits_completed_appointments(db_session, patient, provider):
    _appointment(db_session, patient, provider, minutes_from_now=-90, reason="Old vision exam")
    _appointment(db_session, patient, provider, minutes_from_now=90, reason="Upcoming physical")

    prompt = build_system_prompt(patient, db_session)

    assert "Upcoming physical" in prompt
    assert "Old vision exam" not in prompt


def test_system_prompt_completes_past_appointments_first(db_session, patient, provider):
    appointment = _appointment(db_session, patient, provider, minutes_from_now=-90)

    build_system_prompt(patient, db_session)

    db_session.refresh(appointment)
    assert appointment.status == AppointmentStatus.completed


def test_system_prompt_lists_none_when_only_past_appointments(db_session, patient, provider):
    _appointment(db_session, patient, provider, minutes_from_now=-90)

    assert "None." in build_system_prompt(patient, db_session)


def test_cancel_rejects_a_completed_appointment(db_session, patient, provider):
    appointment = _appointment(
        db_session, patient, provider, minutes_from_now=-90, status=AppointmentStatus.completed
    )

    result = _execute_cancel_appointment({"appointment_id": appointment.id}, patient, db_session)

    assert result["status"] == "error"
    db_session.refresh(appointment)
    assert appointment.status == AppointmentStatus.completed
