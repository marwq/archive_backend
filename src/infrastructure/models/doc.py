from datetime import datetime
import uuid
from typing import Optional

from sqlalchemy import UUID, ForeignKey, Text, func, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base



class Doc(Base):
    __tablename__ = "docs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    chat_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chats.id", name="fk_docs_chat_id"), 
        index=True
    )
    content: Mapped[Optional[str]] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), server_onupdate=func.now())
    
    chat = relationship("Chat", foreign_keys=[chat_id])
