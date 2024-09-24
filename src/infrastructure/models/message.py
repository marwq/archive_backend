from datetime import datetime
import uuid
from typing import Optional

from sqlalchemy import UUID, ForeignKey, Text, func, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .chat import Chat



class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    chat_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chats.id", name="fk_messages_chat_id"), 
        index=True
    )
    is_user: Mapped[bool] = mapped_column(Boolean())
    content: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    
    chat: Mapped[Chat] = relationship(Chat, foreign_keys=[chat_id], lazy="selectin")
