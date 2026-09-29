import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import PasswordResetToken, User
from app.services.auth import hash_password

RESET_TOKEN_TTL = timedelta(minutes=30)

# The raw token is 256 random bits, so a fast hash is enough and lets us look it up by hash
def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def create_reset_token(user: User, db: Session) -> str:
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used_at.is_(None),
    ).delete(synchronize_session=False)

    raw_token = secrets.token_urlsafe(32)
    db.add(PasswordResetToken(
        user_id=user.id,
        token_hash=_hash_token(raw_token),
        expires_at=datetime.now(timezone.utc) + RESET_TOKEN_TTL,
    ))
    db.commit()
    return raw_token


def redeem_reset_token(raw_token: str, new_password: str, db: Session) -> bool:
    now = datetime.now(timezone.utc)
    token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == _hash_token(raw_token),
        PasswordResetToken.used_at.is_(None),
        PasswordResetToken.expires_at > now,
    ).first()
    if token is None:
        return False

    token.user.hashed_password = hash_password(new_password)
    token.used_at = now
    db.commit()
    return True
