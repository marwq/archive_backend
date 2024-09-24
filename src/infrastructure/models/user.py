from datetime import datetime
import uuid

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base



class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
