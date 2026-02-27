from sqlalchemy import Column, Integer, String, Boolean, Enum
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