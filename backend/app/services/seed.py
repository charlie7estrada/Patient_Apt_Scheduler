from app.database import SessionLocal
from app.models import User, UserRole
from app.services.auth import hash_password

DEMO_PROVIDER_EMAIL = "demo.provider@patientscheduler.app"
DEMO_PROVIDER_NAME = "Dr. Demo"


def seed_demo_provider() -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == DEMO_PROVIDER_EMAIL).first()
        if existing:
            return

        provider = User(
            email=DEMO_PROVIDER_EMAIL,
            hashed_password=hash_password("not-used-for-login"),
            full_name=DEMO_PROVIDER_NAME,
            role=UserRole.provider,
        )
        db.add(provider)
        db.commit()
    finally:
        db.close()