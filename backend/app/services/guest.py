import secrets
import uuid
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Appointment, User, UserRole
from app.services.auth import hash_password
from app.services.chat import CLINIC_TZ, _has_conflicting_appointment, _validate_scheduled_at
from app.services.seed import DEMO_PROVIDER_EMAIL

GUEST_EMAIL_DOMAIN = "guest.patientscheduler.app"
GUEST_NAME = "Demo Guest"
GUEST_TTL = timedelta(hours=24)

SAMPLE_REASONS = ["Annual physical", "Follow-up visit"]
SLOT_SEARCH_DAYS = 30

def create_guest_user(db: Session) -> User:
    guest = User(
        email=f"guest-{uuid.uuid4().hex[:12]}@{GUEST_EMAIL_DOMAIN}",
        hashed_password=hash_password(secrets.token_urlsafe(32)),
        full_name=GUEST_NAME,
        role=UserRole.patient,
        is_guest=True,
    )
    db.add(guest)
    db.flush()

    _seed_sample_appointments(guest, db)

    db.commit()
    db.refresh(guest)
    return guest

def _seed_sample_appointments(guest: User, db: Session) -> None:
    provider = db.query(User).filter(User.email == DEMO_PROVIDER_EMAIL).first()
    if provider is None:
        return

    today = datetime.now(CLINIC_TZ).date()
    reasons = iter(SAMPLE_REASONS)
    reason = next(reasons)

    for offset in range(1, SLOT_SEARCH_DAYS + 1):
        slot = _first_open_slot(provider.id, today + timedelta(days=offset), db)
        if slot is None:
            continue

        db.add(Appointment(
            patient_id=guest.id,
            provider_id=provider.id,
            scheduled_at=slot,
            reason=reason,
        ))
        db.flush()

        reason = next(reasons, None)
        if reason is None:
            return


def _first_open_slot(provider_id: int, day: date, db: Session) -> datetime | None:
    for hour in range(9, 17):
        slot = datetime.combine(day, time(hour), tzinfo=CLINIC_TZ)
        if _validate_scheduled_at(slot):
            continue
        if _has_conflicting_appointment(provider_id, slot, db):
            continue
        return slot
    return None


def purge_expired_guests(db: Session) -> int:
    cutoff = datetime.now(timezone.utc) - GUEST_TTL
    expired_ids = [
        user_id
        for (user_id,) in db.query(User.id).filter(
            User.is_guest.is_(True),
            User.created_at < cutoff,
        )
    ]
    if not expired_ids:
        return 0

    db.query(Appointment).filter(Appointment.patient_id.in_(expired_ids)).delete(synchronize_session=False)
    db.query(User).filter(User.id.in_(expired_ids)).delete(synchronize_session=False)
    db.commit()
    return len(expired_ids)