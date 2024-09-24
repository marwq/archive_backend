from datetime import datetime
import uuid
from typing import Optional

from sqlalchemy import UUID, ForeignKey, Text, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base



class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), 
        index=True
    )
    ext: Mapped[str] = mapped_column(String(256))
    title: Mapped[Optional[str]] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    
    user = relationship("User", foreign_keys=[user_id])
