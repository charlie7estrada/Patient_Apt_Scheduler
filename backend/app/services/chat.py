from mistralai import Mistral
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
import json
import os

from app.models import Appointment, AppointmentStatus, User
from app.services.seed import DEMO_PROVIDER_EMAIL

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

CLINIC_TZ = ZoneInfo("America/Chicago")

def build_system_prompt(patient: User, db: Session) -> str:
    today = datetime.now(CLINIC_TZ)

    appointments = (
        db.query(Appointment)
        .filter(Appointment.patient_id == patient.id)
        .filter(Appointment.status != AppointmentStatus.cancelled)
        .order_by(Appointment.scheduled_at)
        .all()
    )

    if appointments:
        appointments_text = "\n".join(
            f"- ID {a.id}: {a.scheduled_at.astimezone(CLINIC_TZ).strftime('%Y-%m-%d %H:%M')} "
            f"({a.scheduled_at.astimezone(CLINIC_TZ).strftime('%A')}) - {a.reason}"
            for a in appointments
        )
    else:
        appointments_text = "None."

    return f"""You are a helpful scheduling assistant for a medical office.
Today's date is {today.strftime('%Y-%m-%d')} ({today.strftime('%A')}).
The office is open Monday-Friday 9am to 5pm, and closed on weekends.
Your job is to help patients book and manage appointments with their healthcare provider.
You can book appointments directly using the create_appointment tool and reschedule / cancel existing ones using the update_appointment tool or cancel_appointment tool — never tell the patient you're unable to do these things.
The patient's current upcoming appointments are:
{appointments_text}
When the patient refers to an existing appointment (e.g. "my Friday appointment"), match it against the list above and use its ID — never ask the patient for an appointment ID directly.
If the patient refers to an appointment that isn't in the list above (for example, because it was already cancelled), tell them you can't find it — never guess or substitute a different appointment's ID.
The ID numbers above are for your internal use only when calling tools — never mention an appointment's ID number to the patient. When describing or listing an appointment for the patient, refer to it by its date, time, and reason instead (e.g. "your vision exam on Thursday, August 27th at 2:00 PM"), formatted the same friendly way you already confirm bookings.
Before calling cancel_appointment, restate the specific appointment (its date, time, and reason) and ask the patient to explicitly confirm — only call the tool after they respond affirmatively (e.g. "yes", "confirm", "that's right"). Never cancel on the first request alone.
Collect the patient's preferred date, time, reason for visit. If any of these are missing, ask the patient for just the missing pieces.
When the patient says something relative like "today", "tomorrow", or "this week", resolve it to an actual date yourself before calling the tool.
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

UPDATE_APPOINTMENT_TOOL = {
    "type": "function",
    "function": {
        "name": "update_appointment",
        "description": "Reschedule an existing appointment for the current patient to a new date, time, and/or reason.",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "integer",
                    "description": "The ID of the appointment to update",
                },
                "date": {
                    "type": "string",
                    "description": "New appointment date in YYYY-MM-DD format",
                },
                "time": {
                    "type": "string",
                    "description": "New appointment time in 24-hour HH:MM format",
                },
                "reason": {
                    "type": "string",
                    "description": "Updated reason for the visit",
                },
            },
            "required": ["appointment_id", "date", "time", "reason"],
        },
    },
}

CANCEL_APPOINTMENT_TOOL = {
    "type": "function",
    "function": {
        "name": "cancel_appointment",
        "description": "Cancel an existing appointment for the current patient.",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "integer",
                    "description": "The ID of the appointment to cancel",
                },
            },
            "required": ["appointment_id"],
        },
    },
}

def _execute_create_appointment(args: dict, patient: User, db: Session) -> dict:
    scheduled_at = datetime.strptime(f"{args['date']} {args['time']}", "%Y-%m-%d %H:%M").replace(tzinfo=CLINIC_TZ)

    error = _validate_scheduled_at(scheduled_at)
    if error:
        return {"status": "error", "message": error}

    provider = db.query(User).filter(User.email == DEMO_PROVIDER_EMAIL).first()

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

def _execute_update_appointment(args: dict, patient: User, db: Session) -> dict:
    appointment = db.query(Appointment).filter(Appointment.id == args["appointment_id"]).first()

    if not appointment or appointment.patient_id != patient.id:
        return {"status": "error", "message": "Appointment not found."}

    scheduled_at = datetime.strptime(
        f"{args['date']} {args['time']}", "%Y-%m-%d %H:%M"
    ).replace(tzinfo=CLINIC_TZ)

    error = _validate_scheduled_at(scheduled_at)
    if error:
        return {"status": "error", "message": error}

    appointment.scheduled_at = scheduled_at
    appointment.reason = args["reason"]
    
    db.commit()
    db.refresh(appointment)

    return {
        "status": "confirmed",
        "appointment_id": appointment.id,
        "scheduled_at": appointment.scheduled_at.isoformat(),
        "provider": appointment.provider.full_name,
    }

def _execute_cancel_appointment(args: dict, patient: User, db: Session) -> dict:
    appointment = db.query(Appointment).filter(Appointment.id == args["appointment_id"]).first()

    if not appointment or appointment.patient_id != patient.id:
        return {"status": "error", "message": "Appointment not found."}

    appointment.status = AppointmentStatus.cancelled
    
    db.commit()
    db.refresh(appointment)

    return {
        "status": "cancelled",
        "appointment_id": appointment.id,
        "provider": appointment.provider.full_name,
    }

def _validate_scheduled_at(scheduled_at: datetime) -> str | None:
    now = datetime.now(CLINIC_TZ)
    if scheduled_at < now:
        return "That date and time is in the past. Please choose a future date and time."
    if scheduled_at.weekday() >= 5:
        return "The clinic is closed on weekends. Please choose a weekday."
    if not (9 <= scheduled_at.hour < 17):
        return "The clinic is only open from 9 AM to 5 PM. Please choose a time in that range."
    return None

TOOL_EXECUTORS = {
    "create_appointment": _execute_create_appointment,
    "update_appointment": _execute_update_appointment,
    "cancel_appointment": _execute_cancel_appointment,
}

def get_chat_response(message: str, history: list, patient: User, db: Session) -> str:
    messages = [{"role": "system", "content": build_system_prompt(patient, db)}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=messages,
        tools=[CREATE_APPOINTMENT_TOOL, UPDATE_APPOINTMENT_TOOL, CANCEL_APPOINTMENT_TOOL],
        tool_choice="auto",
    )

    reply = response.choices[0].message

    if reply.tool_calls:
        messages.append(reply)

        for tool_call in reply.tool_calls:
            args = json.loads(tool_call.function.arguments)
            executor = TOOL_EXECUTORS[tool_call.function.name]
            result = executor(args, patient, db)
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