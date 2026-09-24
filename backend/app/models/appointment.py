from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, false
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class AppointmentStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    reason = Column(String, nullable=True)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.pending)
    is_archived = Column(Boolean, nullable=False, default=False, server_default=false())

    patient = relationship("User", foreign_keys=[patient_id])
    provider = relationship("User", foreign_keys=[provider_id])