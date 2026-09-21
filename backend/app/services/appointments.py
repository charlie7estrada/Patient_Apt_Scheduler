from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models import Appointment, AppointmentStatus

CLINIC_TZ = ZoneInfo("America/Chicago")
APPOINTMENT_DURATION = timedelta(minutes=30)
SLOT_INTERVAL_MINUTES = 15
CLINIC_OPEN_HOUR = 9
CLINIC_CLOSE_HOUR = 17


def complete_past_appointments(db: Session) -> int:
    cutoff = datetime.now(CLINIC_TZ) - APPOINTMENT_DURATION

    completed = (
        db.query(Appointment)
        .filter(
            Appointment.scheduled_at < cutoff,
            Appointment.status.notin_([AppointmentStatus.cancelled, AppointmentStatus.completed]),
        )
        .update({Appointment.status: AppointmentStatus.completed}, synchronize_session=False)
    )
    if completed:
        db.commit()
    return completed
