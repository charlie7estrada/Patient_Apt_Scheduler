from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index, func
from app.database import Base

# One row per chat message, so the rate limit can count messages in a sliding window
class ChatMessageLog(Base):
    __tablename__ = "chat_message_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_chat_message_log_user_id_created_at", "user_id", "created_at"),
    )
