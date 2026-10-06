from datetime import datetime, timedelta, timezone

import pytest

from app.models import ChatMessageLog, User, UserRole
from app.services.auth import hash_password
from app.services.rate_limit import (
    GUEST_CHAT_LIMIT,
    REGISTERED_CHAT_LIMIT,
    refund_chat_message,
    reserve_chat_message,
)


@pytest.fixture()
def guest(db_session):
    guest = User(
        email="guest-test@guest.patientscheduler.app",
        hashed_password=hash_password("not-used-for-login"),
        full_name="Demo Guest",
        role=UserRole.patient,
        is_guest=True,
    )
    db_session.add(guest)
    db_session.commit()
    db_session.refresh(guest)
    return guest


def _logged_messages(user, db):
    return db.query(ChatMessageLog).filter(ChatMessageLog.user_id == user.id).count()


def test_guest_is_blocked_after_limit(db_session, guest):
    for _ in range(GUEST_CHAT_LIMIT):
        assert reserve_chat_message(guest, db_session) is not None

    assert reserve_chat_message(guest, db_session) is None


def test_rejected_message_leaves_no_row(db_session, guest):
    for _ in range(GUEST_CHAT_LIMIT + 1):
        reserve_chat_message(guest, db_session)

    assert _logged_messages(guest, db_session) == GUEST_CHAT_LIMIT


def test_messages_outside_window_do_not_count(db_session, guest):
    over_an_hour_ago = datetime.now(timezone.utc) - timedelta(minutes=61)
    db_session.add_all([
        ChatMessageLog(user_id=guest.id, created_at=over_an_hour_ago)
        for _ in range(GUEST_CHAT_LIMIT)
    ])
    db_session.commit()

    assert reserve_chat_message(guest, db_session) is not None


def test_registered_user_gets_higher_limit(db_session, patient):
    for _ in range(REGISTERED_CHAT_LIMIT):
        assert reserve_chat_message(patient, db_session) is not None

    assert reserve_chat_message(patient, db_session) is None


def test_refund_frees_the_slot(db_session, guest):
    for _ in range(GUEST_CHAT_LIMIT - 1):
        reserve_chat_message(guest, db_session)
    last = reserve_chat_message(guest, db_session)

    refund_chat_message(last, db_session)

    assert _logged_messages(guest, db_session) == GUEST_CHAT_LIMIT - 1
    assert reserve_chat_message(guest, db_session) is not None


def test_limit_is_per_user(db_session, guest, patient):
    for _ in range(GUEST_CHAT_LIMIT):
        reserve_chat_message(guest, db_session)

    assert reserve_chat_message(patient, db_session) is not None
