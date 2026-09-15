import secrets
import uuid

from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.services.auth import hash_password

GUEST_EMAIL_DOMAIN = "guest.patientscheduler.app"
GUEST_NAME = "Demo Guest"


def create_guest_user(db: Session) -> User:
    guest = User(
        email=f"guest-{uuid.uuid4().hex[:12]}@{GUEST_EMAIL_DOMAIN}",
        hashed_password=hash_password(secrets.token_urlsafe(32)),
        full_name=GUEST_NAME,
        role=UserRole.patient,
        is_guest=True,
    )
    db.add(guest)
    db.commit()
    db.refresh(guest)
    return guest
