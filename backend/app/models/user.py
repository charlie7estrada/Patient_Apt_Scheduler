from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, false, func
from app.database import Base
import enum

class UserRole(enum.Enum):
    patient = "patient"
    provider = "provider"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    is_guest = Column(Boolean, nullable=False, default=False, server_default=false())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())