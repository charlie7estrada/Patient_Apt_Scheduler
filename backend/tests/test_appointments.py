from datetime import datetime, timedelta

from app.models import Appointment, AppointmentStatus, User, UserRole
from app.services.chat import (
    CLINIC_TZ,
    _execute_cancel_appointment,
    _execute_create_appointment,
    _execute_update_appointment,
)


def _next_weekday_at(hour: int, weekday: int, minute: int = 0) -> datetime:
    now = datetime.now(CLINIC_TZ)
    days_ahead = (weekday - now.weekday()) % 7
    days_ahead = days_ahead if days_ahead > 0 else days_ahead + 7
    target = now + timedelta(days=days_ahead)
    return target.replace(hour=hour, minute=minute, second=0, microsecond=0)


def _next_valid_slot() -> tuple[str, str]:
    dt = _next_weekday_at(hour=10, weekday=0)  # next Monday, 10am
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M")


def _other_patient(db_session) -> User:
    other = User(
        email="other@example.com",
        hashed_password="x",
        full_name="Other Patient",
        role=UserRole.patient,
    )
    db_session.add(other)
    db_session.commit()
    db_session.refresh(other)
    return other


def test_create_appointment_success(db_session, patient, provider):
    date, time = _next_valid_slot()
    result = _execute_create_appointment(
        {"date": date, "time": time, "reason": "Checkup"}, patient, db_session
    )

    assert result["status"] == "confirmed"
    assert result["provider"] == provider.full_name

    saved = db_session.query(Appointment).one()
    assert saved.status == AppointmentStatus.confirmed


def test_create_appointment_rejects_invalid_time(db_session, patient, provider):
    result = _execute_create_appointment(
        {"date": "2020-01-01", "time": "10:00", "reason": "Checkup"}, patient, db_session
    )

    assert result["status"] == "error"
    assert db_session.query(Appointment).count() == 0


def test_update_appointment_changes_time(db_session, patient, provider):
    date, time = _next_valid_slot()
    created = _execute_create_appointment(
        {"date": date, "time": time, "reason": "Checkup"}, patient, db_session
    )

    new_dt = _next_weekday_at(hour=14, weekday=1)  # next Tuesday, 2pm
    result = _execute_update_appointment(
        {
            "appointment_id": created["appointment_id"],
            "date": new_dt.strftime("%Y-%m-%d"),
            "time": "14:00",
            "reason": "Follow-up",
        },
        patient,
        db_session,
    )

    assert result["status"] == "confirmed"
    assert result["scheduled_at"].startswith(new_dt.strftime("%Y-%m-%d"))


def test_update_appointment_rejects_invalid_time(db_session, patient, provider):
    date, time = _next_valid_slot()
    created = _execute_create_appointment(
        {"date": date, "time": time, "reason": "Checkup"}, patient, db_session
    )

    result = _execute_update_appointment(
        {
            "appointment_id": created["appointment_id"],
            "date": "2020-01-01",
            "time": "10:00",
            "reason": "Follow-up",
        },
        patient,
        db_session,
    )

    assert result["status"] == "error"


def test_update_appointment_rejects_other_patients_appointment(db_session, patient, provider):
    date, time = _next_valid_slot()
    created = _execute_create_appointment(
        {"date": date, "time": time, "reason": "Checkup"}, patient, db_session
    )
    other = _other_patient(db_session)

    result = _execute_update_appointment(
        {
            "appointment_id": created["appointment_id"],
            "date": date,
            "time": time,
            "reason": "Hijack attempt",
        },
        other,
        db_session,
    )

    assert result["status"] == "error"


def test_cancel_appointment_marks_cancelled(db_session, patient, provider):
    date, time = _next_valid_slot()
    created = _execute_create_appointment(
        {"date": date, "time": time, "reason": "Checkup"}, patient, db_session
    )

    result = _execute_cancel_appointment(
        {"appointment_id": created["appointment_id"]}, patient, db_session
    )

    assert result["status"] == "cancelled"

    cancelled = db_session.query(Appointment).filter(
        Appointment.id == created["appointment_id"]
    ).first()
    assert cancelled.status.value == "cancelled"


def test_cancel_appointment_rejects_other_patients_appointment(db_session, patient, provider):
    date, time = _next_valid_slot()
    created = _execute_create_appointment(
        {"date": date, "time": time, "reason": "Checkup"}, patient, db_session
    )
    other = _other_patient(db_session)

    result = _execute_cancel_appointment(
        {"appointment_id": created["appointment_id"]}, other, db_session
    )

    assert result["status"] == "error"


def test_create_appointment_rejects_conflicting_slot(db_session, patient, provider):
    date, time = _next_valid_slot()
    _execute_create_appointment(
        {"date": date, "time": time, "reason": "Checkup"}, patient, db_session
    )

    other = _other_patient(db_session)
    result = _execute_create_appointment(
        {"date": date, "time": time, "reason": "Follow-up"}, other, db_session
    )

    assert result["status"] == "error"


def test_create_appointment_allows_different_times(db_session, patient, provider):
    date, time = _next_valid_slot()
    first = _execute_create_appointment(
        {"date": date, "time": time, "reason": "Checkup"}, patient, db_session
    )

    other = _other_patient(db_session)
    other_dt = _next_weekday_at(hour=11, weekday=0)
    second = _execute_create_appointment(
        {"date": other_dt.strftime("%Y-%m-%d"), "time": "11:00", "reason": "Follow-up"}, other, db_session
    )

    assert first["status"] == "confirmed"
    assert second["status"] == "confirmed"


def test_create_appointment_allows_slot_freed_by_cancellation(db_session, patient, provider):
    date, time = _next_valid_slot()
    created = _execute_create_appointment(
        {"date": date, "time": time, "reason": "Checkup"}, patient, db_session
    )
    _execute_cancel_appointment({"appointment_id": created["appointment_id"]}, patient, db_session)

    other = _other_patient(db_session)
    result = _execute_create_appointment(
        {"date": date, "time": time, "reason": "Follow-up"}, other, db_session
    )

    assert result["status"] == "confirmed"


def test_update_appointment_rejects_conflicting_slot(db_session, patient, provider):
    date, time = _next_valid_slot()
    created = _execute_create_appointment(
        {"date": date, "time": time, "reason": "Checkup"}, patient, db_session
    )

    other = _other_patient(db_session)
    other_dt = _next_weekday_at(hour=11, weekday=0)
    _execute_create_appointment(
        {"date": other_dt.strftime("%Y-%m-%d"), "time": "11:00", "reason": "Follow-up"}, other, db_session
    )

    result = _execute_update_appointment(
        {
            "appointment_id": created["appointment_id"],
            "date": other_dt.strftime("%Y-%m-%d"),
            "time": "11:00",
            "reason": "Trying to steal the slot",
        },
        patient,
        db_session,
    )

    assert result["status"] == "error"


def test_update_appointment_allows_keeping_same_time(db_session, patient, provider):
    date, time = _next_valid_slot()
    created = _execute_create_appointment(
        {"date": date, "time": time, "reason": "Checkup"}, patient, db_session
    )

    result = _execute_update_appointment(
        {
            "appointment_id": created["appointment_id"],
            "date": date,
            "time": time,
            "reason": "Updated reason, same time",
        },
        patient,
        db_session,
    )

    assert result["status"] == "confirmed"

def test_update_appointment_confirms_a_completed_appointment(db_session, patient, provider):
    date, time = _next_valid_slot()
    created = _execute_create_appointment(
        {"date": date, "time": time, "reason": "Checkup"}, patient, db_session
    )
    appointment = db_session.query(Appointment).one()
    appointment.status = AppointmentStatus.completed
    db_session.commit()

    later = _next_weekday_at(hour=15, weekday=2)
    result = _execute_update_appointment(
        {
            "appointment_id": created["appointment_id"],
            "date": later.strftime("%Y-%m-%d"),
            "time": "15:00",
            "reason": "Rebooked after missing it",
        },
        patient,
        db_session,
    )

    assert result["status"] == "confirmed"
    db_session.refresh(appointment)
    assert appointment.status == AppointmentStatus.confirmed

def test_create_appointment_rejects_overlapping_slot(db_session, patient, provider):
    date = _next_weekday_at(hour=10, weekday=0).strftime("%Y-%m-%d")
    _execute_create_appointment(
        {"date": date, "time": "10:00", "reason": "Checkup"}, patient, db_session
    )

    other = _other_patient(db_session)
    result = _execute_create_appointment(
        {"date": date, "time": "10:15", "reason": "Follow-up"}, other, db_session
    )

    assert result["status"] == "error"


def test_create_appointment_rejects_slot_that_starts_before_an_existing_one(db_session, patient, provider):
    date = _next_weekday_at(hour=10, weekday=0).strftime("%Y-%m-%d")
    _execute_create_appointment(
        {"date": date, "time": "10:30", "reason": "Checkup"}, patient, db_session
    )

    other = _other_patient(db_session)
    result = _execute_create_appointment(
        {"date": date, "time": "10:15", "reason": "Follow-up"}, other, db_session
    )

    assert result["status"] == "error"


def test_create_appointment_allows_back_to_back_slots(db_session, patient, provider):
    date = _next_weekday_at(hour=10, weekday=0).strftime("%Y-%m-%d")
    first = _execute_create_appointment(
        {"date": date, "time": "10:00", "reason": "Checkup"}, patient, db_session
    )

    other = _other_patient(db_session)
    second = _execute_create_appointment(
        {"date": date, "time": "10:30", "reason": "Follow-up"}, other, db_session
    )

    assert first["status"] == "confirmed"
    assert second["status"] == "confirmed"


def test_update_appointment_rejects_overlapping_slot(db_session, patient, provider):
    date = _next_weekday_at(hour=10, weekday=0).strftime("%Y-%m-%d")

    other = _other_patient(db_session)
    _execute_create_appointment(
        {"date": date, "time": "10:00", "reason": "Checkup"}, other, db_session
    )
    mine = _execute_create_appointment(
        {"date": date, "time": "14:00", "reason": "Follow-up"}, patient, db_session
    )

    result = _execute_update_appointment(
        {
            "appointment_id": mine["appointment_id"],
            "date": date,
            "time": "10:15",
            "reason": "Follow-up",
        },
        patient,
        db_session,
    )

    assert result["status"] == "error"


def test_update_appointment_allows_shifting_within_its_own_window(db_session, patient, provider):
    date = _next_weekday_at(hour=10, weekday=0).strftime("%Y-%m-%d")
    mine = _execute_create_appointment(
        {"date": date, "time": "10:00", "reason": "Checkup"}, patient, db_session
    )

    result = _execute_update_appointment(
        {
            "appointment_id": mine["appointment_id"],
            "date": date,
            "time": "10:15",
            "reason": "Checkup",
        },
        patient,
        db_session,
    )

    assert result["status"] == "confirmed"

def test_new_appointment_is_not_archived(db_session, patient, provider):
    date, time = _next_valid_slot()
    created = _execute_create_appointment(
        {"date": date, "time": time, "reason": "Checkup"}, patient, db_session
    )

    appointment = db_session.query(Appointment).filter(
        Appointment.id == created["appointment_id"]
    ).one()

    assert appointment.is_archived is False
