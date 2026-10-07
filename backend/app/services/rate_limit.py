from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import ChatMessageLog, User

CHAT_WINDOW = timedelta(hours=1)
GUEST_CHAT_LIMIT = 20
REGISTERED_CHAT_LIMIT = 100
CHAT_LIMIT_MESSAGE = "Message limit reached! Feel free to try again in an hour."


def chat_limit_for(user: User) -> int:
    return GUEST_CHAT_LIMIT if user.is_guest else REGISTERED_CHAT_LIMIT


# Reserve first, then count with our own row included. Two requests racing for the
# last slot each see the other's row and both back out, so the cap is never exceeded.
def reserve_chat_message(user: User, db: Session) -> ChatMessageLog | None:
    now = datetime.now(timezone.utc)
    reservation = ChatMessageLog(user_id=user.id, created_at=now)
    db.add(reservation)
    db.commit()

    used = db.query(ChatMessageLog).filter(
        ChatMessageLog.user_id == user.id,
        ChatMessageLog.created_at > now - CHAT_WINDOW,
    ).count()
    if used > chat_limit_for(user):
        db.delete(reservation)
        db.commit()
        return None

    return reservation


# Called when the chat fails so the patient isn't charged for a message that got no reply.
# Rolls back first in case the failure left the session unusable.
def refund_chat_message(reservation: ChatMessageLog, db: Session) -> None:
    db.rollback()
    db.delete(reservation)
    db.commit()
