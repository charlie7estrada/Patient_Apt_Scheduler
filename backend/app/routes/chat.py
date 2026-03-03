from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chat import get_chat_response

router = APIRouter(prefix="/chat", tags=["chat"])

class Message(BaseModel):
    text: str
    history: list = []

@router.post("/")
def chat(message: Message):
    try:
        response = get_chat_response(message.text, message.history)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))