"""This module contains the implementation of the user repository."""
from datetime import date, datetime, timedelta
from typing import Sequence

from sqlalchemy import select, insert, update

from src.infrastructure.models import Chat, DocVersion, DocOrigin, Message
from src.infrastructure.repositories.base import SQLAlchemyRepo


class ChatRepo(SQLAlchemyRepo[Chat]):
    """Chat repository implementation for SQLAlchemy ORM."""
    
    model = Chat
    
    async def create_chat(self, user_id: str) -> Chat:
        chat = Chat(user_id=user_id)
        self._session.add(chat)
        await self._session.commit()
        await self._session.refresh(chat)
        return chat
    
    async def create_doc_origin(self, is_archive: bool, ext: str, content: str | None = None) -> DocOrigin:
        doc_origin = DocOrigin(is_archive=is_archive, content=content, ext=ext)
        self._session.add(doc_origin)
        await self._session.commit()
        await self._session.refresh(doc_origin)
        return doc_origin
    
    async def create_doc_version(self, chat_id: str, doc_origin_id: str, content: str | None = None) -> DocVersion:
        doc_version = DocVersion(content=content, chat_id=chat_id, doc_origin_id=doc_origin_id)
        self._session.add(doc_version)
        await self._session.commit()
        await self._session.refresh(doc_version)
        return doc_version
    
    async def edit_doc_version(self, doc_version_id: str, content: str) -> DocVersion:
        stmt = (
            update(DocVersion)
            .where(DocVersion.id == doc_version_id)
            .values(dict(content=content))
            .returning(DocVersion)
        )
        resp = await self._session.execute(stmt)
        await self._session.commit()
        return resp.scalar()
        
    async def edit_doc_origin(self, doc_origin_id: str, content: str) -> None:
        stmt = (
            update(DocOrigin)
            .where(DocOrigin.id == doc_origin_id)
            .values(dict(content=content))
        )
        await self._session.execute(stmt)
        await self._session.commit()