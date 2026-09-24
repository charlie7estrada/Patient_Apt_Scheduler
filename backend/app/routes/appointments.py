from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Appointment, AppointmentStatus, User
from app.services.auth import get_current_user
from app.services.appointments import complete_past_appointments


router = APIRouter(prefix="/appointments", tags=["appointments"])

ARCHIVABLE_STATUSES = (AppointmentStatus.cancelled, AppointmentStatus.completed)

@router.get("/")
def list_appointments(
    include_archived: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    complete_past_appointments(db)
    
    query = db.query(Appointment).filter(Appointment.patient_id == current_user.id)
    if not include_archived:
        query = query.filter(Appointment.is_archived.is_(False))

    appointments = query.order_by(Appointment.scheduled_at).all()

    return [
        {
            "id": a.id,
            "scheduled_at": a.scheduled_at,
            "reason": a.reason,
            "status": a.status.value,
            "provider_name": a.provider.full_name,
            "is_archived": a.is_archived,
        }
        for a in appointments
    ]


@router.post("/{appointment_id}/archive", status_code=status.HTTP_204_NO_CONTENT)
def archive_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # An appointment that just slipped into the past should be archivable
    # without the patient having to reload first.
    complete_past_appointments(db)

    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id, Appointment.patient_id == current_user.id)
        .first()
    )
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment.status not in ARCHIVABLE_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Only cancelled or completed appointments can be archived.",
        )

    appointment.is_archived = True
    db.commit()
