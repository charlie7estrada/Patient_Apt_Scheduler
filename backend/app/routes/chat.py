from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging
from app.database import get_db
from app.services.chat import get_chat_response, ChatUnavailableError
from app.services.auth import get_current_user
from app.services.rate_limit import (
    CHAT_LIMIT_MESSAGE,
    CHAT_WINDOW,
    refund_chat_message,
    reserve_chat_message,
)
from app.models import ChatMessageLog, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

class Message(BaseModel):
    text: str
    history: list = []

# A failed refund only costs the patient one slot, so it shouldn't replace the real error response
def _refund(reservation: ChatMessageLog, db: Session) -> None:
    try:
        refund_chat_message(reservation, db)
    except Exception:
        logger.exception("Failed to refund chat rate limit reservation")

@router.post("/")
def chat(
    message: Message, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ):
    reservation = reserve_chat_message(current_user, db)
    if reservation is None:
        raise HTTPException(
            status_code=429,
            detail=CHAT_LIMIT_MESSAGE,
            headers={"Retry-After": str(int(CHAT_WINDOW.total_seconds()))},
        )
    
    try:
        response = get_chat_response(message.text, message.history, current_user, db)
        return {"response": response}
    except ChatUnavailableError as e:
        _refund(reservation, db)
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        logger.exception("Unhandled error in chat endpoint")
        _refund(reservation, db)
        raise HTTPException(
            status_code=500, detail="Something went wrong. Please try again."
        ) 