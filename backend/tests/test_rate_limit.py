from datetime import datetime, timedelta, timezone

import pytest
from starlette.requests import Request

from app.models import ChatMessageLog, GuestCreationLog, User, UserRole
from app.services.auth import hash_password
from app.services.rate_limit import (
    GUEST_CHAT_LIMIT,
    GUEST_CREATION_LIMIT,
    REGISTERED_CHAT_LIMIT,
    client_ip,
    refund_chat_message,
    refund_guest_creation,
    reserve_chat_message,
    reserve_guest_creation,
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




def _request(true_client_ip=None, host="10.0.0.1"):
    headers = [(b"true-client-ip", true_client_ip.encode())] if true_client_ip else []
    return Request({"type": "http", "headers": headers, "client": (host, 12345)})


def test_client_ip_prefers_true_client_ip_header():
    assert client_ip(_request(true_client_ip="203.0.113.7")) == "203.0.113.7"


def test_client_ip_falls_back_to_connection_address():
    assert client_ip(_request()) == "10.0.0.1"


def test_ip_is_blocked_after_guest_creation_limit(db_session):
    for _ in range(GUEST_CREATION_LIMIT):
        assert reserve_guest_creation("203.0.113.7", db_session) is not None

    assert reserve_guest_creation("203.0.113.7", db_session) is None
    assert db_session.query(GuestCreationLog).count() == GUEST_CREATION_LIMIT


def test_guest_creation_limit_is_per_ip(db_session):
    for _ in range(GUEST_CREATION_LIMIT):
        reserve_guest_creation("203.0.113.7", db_session)

    assert reserve_guest_creation("198.51.100.4", db_session) is not None


def test_guest_creation_refund_frees_the_slot(db_session):
    for _ in range(GUEST_CREATION_LIMIT - 1):
        reserve_guest_creation("203.0.113.7", db_session)
    last = reserve_guest_creation("203.0.113.7", db_session)

    refund_guest_creation(last, db_session)

    assert reserve_guest_creation("203.0.113.7", db_session) is not None
    