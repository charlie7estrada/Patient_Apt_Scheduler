from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models import User, UserRole
from app.services.auth import hash_password, verify_password, create_access_token
from app.services.guest import create_guest_user
from app.services.password_reset import create_reset_token, redeem_reset_token
from app.services.email import build_reset_link, send_password_reset_email
from app.services.rate_limit import (
    GUEST_CREATION_LIMIT_MESSAGE,
    GUEST_CREATION_WINDOW,
    client_ip,
    refund_guest_creation,
    reserve_guest_creation,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully", "id": user.id}

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.email, "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/guest", status_code=status.HTTP_201_CREATED)
def guest_login(request: Request, db: Session = Depends(get_db)):
    reservation = reserve_guest_creation(client_ip(request), db)
    if reservation is None:
        raise HTTPException(
            status_code=429,
            detail=GUEST_CREATION_LIMIT_MESSAGE,
            headers={"Retry-After": str(int(GUEST_CREATION_WINDOW.total_seconds()))},
        )

    try:
        guest = create_guest_user(db)
    except Exception:
        logger.exception("Failed to create guest account")
        try:
            refund_guest_creation(reservation, db)
        except Exception:
            logger.exception("Failed to refund guest creation reservation")
        raise HTTPException(status_code=500, detail="Could not start the demo. Please try again.")
    
    token = create_access_token({"sub": guest.email, "role": guest.role.value, "guest": True})
    return {"access_token": token, "token_type": "bearer"}

# Same response whether or not the email exists, so this can't be used to probe for accounts
@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
def forgot_password(data: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user and not user.is_guest:
        raw_token = create_reset_token(user, db)
        background_tasks.add_task(send_password_reset_email, user.email, build_reset_link(raw_token))
    return {"message": "If that email is registered, a reset link is on its way."}

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    if not redeem_reset_token(data.token, data.new_password, db):
        raise HTTPException(status_code=400, detail="This reset link is invalid or has expired")
    return {"message": "Password updated"}
