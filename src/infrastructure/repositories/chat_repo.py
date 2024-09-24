"""This module contains the implementation of the user repository."""
from datetime import date, datetime, timedelta
from typing import Sequence


from src.infrastructure.models import Chat
from src.infrastructure.repositories.base import SQLAlchemyRepo


class ChatRepo(SQLAlchemyRepo[Chat]):
    """Chat repository implementation for SQLAlchemy ORM."""
    
    model = Chat
    
    async def create_chat(self, user_id: str, ext: str) -> Chat:
        chat = Chat(user_id=user_id, ext=ext)
        self._session.add(chat)
        await self._session.commit()
        await self._session.refresh(chat)
        return chat
