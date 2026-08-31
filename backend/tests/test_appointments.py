from datetime import datetime, timedelta

from app.models import Appointment, User, UserRole
from app.services.chat import (
    CLINIC_TZ,
    _execute_cancel_appointment,
    _execute_create_appointment,
    _execute_update_appointment,
)


def _next_weekday_at(hour: int, weekday: int) -> datetime:
    now = datetime.now(CLINIC_TZ)
    days_ahead = (weekday - now.weekday()) % 7
    days_ahead = days_ahead if days_ahead > 0 else days_ahead + 7
    target = now + timedelta(days=days_ahead)
    return target.replace(hour=hour, minute=0, second=0, microsecond=0)


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
