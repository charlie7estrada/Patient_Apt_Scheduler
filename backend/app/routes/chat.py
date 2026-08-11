from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.chat import get_chat_response
from app.services.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/chat", tags=["chat"])

class Message(BaseModel):
    text: str
    history: list = []

@router.post("/")
def chat(
    message: Message, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ):
    try:
        response = get_chat_response(message.text, message.history, current_user, db)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))