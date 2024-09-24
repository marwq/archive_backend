from __future__ import annotations
from datetime import datetime
import uuid
from typing import Optional

from sqlalchemy import UUID, ForeignKey, Text, func, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .chat import Chat



class DocVersion(Base):
    __tablename__ = "doc_verions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    content: Mapped[Optional[str]] = mapped_column(Text())
    chat_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chats.id", name="fk_doc_versions_chat_id"), 
        index=True,
    )
    doc_origin_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("doc_origins.id", name="fk_doc_versions_doc_origin_id"), 
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_onupdate=func.now(), server_default=func.now())
    
    chat: Mapped[Chat] = relationship("Chat", back_populates="doc_versions", foreign_keys=[chat_id], lazy="selectin")
    doc_origin: Mapped[DocOrigin] = relationship("DocOrigin", foreign_keys=[doc_origin_id], lazy="selectin")

class DocOrigin(Base):
    __tablename__ = "doc_origins"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    is_archive: Mapped[bool] = mapped_column(Boolean())
    ext: Mapped[str] = mapped_column(String(256))
    content: Mapped[Optional[str]] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_onupdate=func.now(), server_default=func.now())
