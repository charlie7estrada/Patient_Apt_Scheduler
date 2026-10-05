from sqlalchemy import Column, Integer, String, DateTime, Index, func
from app.database import Base

# One row per guest account created, keyed by client IP. Not linked to the guest,
# so purging a guest doesn't reset the IP's count.
class GuestCreationLog(Base):
    __tablename__ = "guest_creation_log"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(45), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_guest_creation_log_ip_created_at", "ip", "created_at"),
    )
