from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Appointment, User
from app.services.auth import get_current_user

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.get("/")
def list_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appointments = (
        db.query(Appointment)
        .filter(Appointment.patient_id == current_user.id)
        .order_by(Appointment.scheduled_at)
        .all()
    )
    return [
        {
            "id": a.id,
            "scheduled_at": a.scheduled_at,
            "reason": a.reason,
            "status": a.status.value,
            "provider_name": a.provider.full_name,
        }
        for a in appointments
    ]