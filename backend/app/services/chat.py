from mistralai import Mistral
from dotenv import load_dotenv
import os

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

SYSTEM_PROMPT = """You are a helpful scheduling assistant for a medical office.
Your job is to help patients book appointments with their healthcare provider.
Collect the patient's preferred date, time, reason for visit, and any provider preference.
Once you have all details, summarize and ask them to confirm.
Keep responses short, friendly, and professional."""

def get_chat_response(message: str, history: list) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=messages
    )
    return response.choices[0].message.content