import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

def build_reset_link(raw_token: str) -> str:
    return f"{FRONTEND_URL}/reset-password?token={raw_token}"


# No email provider yet, so the link goes to the server log. Logged at warning because
# uvicorn only prints app logs at warning and above by default.
def send_password_reset_email(to: str, reset_link: str) -> None:
    logger.warning("Password reset link for %s: %s", to, reset_link)
