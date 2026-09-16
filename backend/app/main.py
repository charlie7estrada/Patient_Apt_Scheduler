from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes import auth, chat, appointments
from app.services.seed import seed_demo_provider
from app.services.guest import purge_expired_guests
from app.database import SessionLocal
from app.services.appointments import complete_past_appointments

import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_demo_provider()
    db = SessionLocal()
    try:
        purge_expired_guests(db)
        complete_past_appointments(db)
    finally:
        db.close()
    yield

app = FastAPI(title="Patient Appointment Scheduler API", lifespan=lifespan)

origins = [
    "http://localhost:5173",
    os.getenv("FRONTEND_URL", ""),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}