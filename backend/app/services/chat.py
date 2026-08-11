from mistralai import Mistral
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy.orm import Session
import json
import os

from app.models import Appointment, User
from app.services.seed import DEMO_PROVIDER_EMAIL

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

SYSTEM_PROMPT = """You are a helpful scheduling assistant for a medical office.
Your job is to help patients book appointments with their healthcare provider.
Collect the patient's preferred date, time, reason for visit.
Once you have all three details, call the create_appointment tool to book it.
After the tool returns, confirm the booking to the patient in a short, friendly message.
Keep responses short, friendly, and professional."""

CREATE_APPOINTMENT_TOOL = {
    "type": "function",
    "function": {
        "name": "create_appointment",
        "description": "Book a medical appointment for the current patient once date, time, and reason are known.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Appointment date in YYYY-MM-DD format",
                },
                "time": {
                    "type": "string",
                    "description": "Appointment time in 24-hour HH:MM format",
                },
                "reason": {
                    "type": "string",
                    "description": "Brief reason for the visit",
                },
            },
            "required": ["date", "time", "reason"],
        },
    },
}

def _execute_create_appointment(args: dict, patient: User, db: Session) -> dict:
    provider = db.query(User).filter(User.email == DEMO_PROVIDER_EMAIL).first()
    scheduled_at = datetime.strptime(f"{args['date']} {args['time']}", "%Y-%m-%d %H:%M")

    appointment = Appointment(
        patient_id=patient.id,
        provider_id=provider.id,
        scheduled_at=scheduled_at,
        reason=args["reason"],
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return {
        "status": "confirmed",
        "appointment_id": appointment.id,
        "scheduled_at": scheduled_at.isoformat(),
        "provider": provider.full_name,
    }

def get_chat_response(message: str, history: list, patient: User, db: Session) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=messages,
        tools=[CREATE_APPOINTMENT_TOOL],
        tool_choice="auto",
    )

    reply = response.choices[0].message

    if reply.tool_calls:
        messages.append(reply)

        for tool_call in reply.tool_calls:
            args = json.loads(tool_call.function.arguments)
            result = _execute_create_appointment(args, patient, db)
            messages.append({
                "role": "tool",
                "name": tool_call.function.name,
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })

        follow_up = client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
        )
        return follow_up.choices[0].message.content
    
    return reply.content