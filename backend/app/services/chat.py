from mistralai import Mistral
from mistralai.models import SDKError
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy.orm import Session
import json
import logging
import os

from app.models import Appointment, AppointmentStatus, User
from app.services.seed import DEMO_PROVIDER_EMAIL
from app.services.appointments import (
    APPOINTMENT_DURATION,
    CLINIC_CLOSE_HOUR,
    CLINIC_OPEN_HOUR,
    SLOT_INTERVAL_MINUTES,
    CLINIC_TZ,
    complete_past_appointments,
)

load_dotenv()

logger = logging.getLogger(__name__)

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

class ChatUnavailableError(Exception):
    """Raised when the AI provider is unreachable, rate limited, or errored."""

RATE_LIMIT_MESSAGE = (
    "I'm getting more requests than I can handle right now. "
    "Please wait a moment and try again."
)

UNAVAILABLE_MESSAGE = (
    "I'm having trouble connecting right now. Please try again in a moment."
)

MISTRAL_TIMEOUT_MS = 30_000


def _complete(**kwargs):
    """Call Mistral, converting provider failures into ChatUnavailableError."""
    try:
        return client.chat.complete(timeout_ms=MISTRAL_TIMEOUT_MS, **kwargs)
    except SDKError as e:
        status = e.raw_response.status_code
        logger.warning(
            "Mistral API error: status=%s body=%s", status, e.raw_response.text[:500]
        )
        if status == 429:
            raise ChatUnavailableError(RATE_LIMIT_MESSAGE) from e
        raise ChatUnavailableError(UNAVAILABLE_MESSAGE) from e
    except Exception as e:
        logger.exception("Unexpected error calling Mistral")
        raise ChatUnavailableError(UNAVAILABLE_MESSAGE) from e

def build_system_prompt(patient: User, db: Session) -> str:
    today = datetime.now(CLINIC_TZ)

    complete_past_appointments(db)

    appointments = (
        db.query(Appointment)
        .filter(Appointment.patient_id == patient.id)
        .filter(Appointment.status.notin_([AppointmentStatus.cancelled, AppointmentStatus.completed]))
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

    if _has_conflicting_appointment(provider.id, scheduled_at, db):
        return {"status": "error", "message": "That time is no longer available. Please choose a different time."}

    appointment = Appointment(
        patient_id=patient.id,
        provider_id=provider.id,
        scheduled_at=scheduled_at,
        reason=args["reason"],
        status=AppointmentStatus.confirmed,
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

    if _has_conflicting_appointment(appointment.provider_id, scheduled_at, db, exclude_appointment_id=appointment.id):
        return {"status": "error", "message": "That time is no longer available. Please choose a different time."}

    appointment.scheduled_at = scheduled_at
    appointment.reason = args["reason"]
    appointment.status = AppointmentStatus.confirmed
    
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

    if appointment.status == AppointmentStatus.completed:
        return {"status": "error", "message": "That appointment has already taken place."}

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
    
    opens = scheduled_at.replace(hour=CLINIC_OPEN_HOUR, minute=0)
    closes = scheduled_at.replace(hour=CLINIC_CLOSE_HOUR, minute=0)
    if scheduled_at < opens or scheduled_at + APPOINTMENT_DURATION > closes:
        return ("Please choose a time between 9 AM and 4:30 PM.") 
            # Appointments run 30 minutes and the clinic closes at 5 PM, so the last one starts at 4:30 PM. 

    if scheduled_at.minute % SLOT_INTERVAL_MINUTES:
        return "Appointments start on the quarter hour: :00, :15, :30, or :45."
    
    return None

def _has_conflicting_appointment(provider_id: int, scheduled_at: datetime, db: Session, exclude_appointment_id: int | None = None) -> bool:
    # Two 30-minute appointments overlap exactly when the existing one starts
    # strictly inside (new start - 30min, new start + 30min).
    window_start = scheduled_at - APPOINTMENT_DURATION
    window_end = scheduled_at + APPOINTMENT_DURATION

    query = db.query(Appointment).filter(
        Appointment.provider_id == provider_id,
        Appointment.scheduled_at > window_start,
        Appointment.scheduled_at < window_end,
        Appointment.status != AppointmentStatus.cancelled,
    )
    if exclude_appointment_id is not None:
        query = query.filter(Appointment.id != exclude_appointment_id)
    return query.first() is not None

TOOL_EXECUTORS = {
    "create_appointment": _execute_create_appointment,
    "update_appointment": _execute_update_appointment,
    "cancel_appointment": _execute_cancel_appointment,
}

def get_chat_response(message: str, history: list, patient: User, db: Session) -> str:
    messages = [{"role": "system", "content": build_system_prompt(patient, db)}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    response = _complete(
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

        follow_up = _complete(
            model="mistral-small-latest",
            messages=messages,
        )
        return follow_up.choices[0].message.content
    
    return reply.content