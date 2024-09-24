"""This module contains the implementation of the user repository."""
from datetime import date, datetime, timedelta
from typing import Sequence

from sqlalchemy import select, insert, update

from src.infrastructure.models import Chat, Doc, Message
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
    
    async def create_doc(self, chat_id: str, content: str | None = None) -> Doc:
        doc = Doc(chat_id=chat_id, content=content)
        self._session.add(doc)
        await self._session.commit()
        await self._session.refresh(doc)
        return doc
    
    async def edit_doc(self, doc_id: str, content: str) -> None:
        stmt = (
            update(Doc)
            .where(Doc.id == doc_id)
            .values(dict(content=content))
        )
        await self._session.execute(stmt)
        await self._session.commit()