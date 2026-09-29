from datetime import datetime, timedelta, timezone

from app.models import PasswordResetToken
from app.services.password_reset import create_reset_token, redeem_reset_token


def test_reset_token_is_single_use(db_session, patient):
    raw_token = create_reset_token(patient, db_session)

    assert redeem_reset_token(raw_token, "brandnewpass456", db_session) is True
    assert redeem_reset_token(raw_token, "anotherpass789", db_session) is False


def test_expired_reset_token_is_rejected(db_session, patient):
    raw_token = create_reset_token(patient, db_session)
    stored = db_session.query(PasswordResetToken).one()
    stored.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()

    assert redeem_reset_token(raw_token, "brandnewpass456", db_session) is False


def test_new_reset_token_invalidates_older_one(db_session, patient):
    first = create_reset_token(patient, db_session)
    second = create_reset_token(patient, db_session)

    assert redeem_reset_token(first, "brandnewpass456", db_session) is False
    assert redeem_reset_token(second, "brandnewpass456", db_session) is True