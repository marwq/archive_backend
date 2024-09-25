"""This module contains the implementation of the user repository."""
from datetime import date, datetime, timedelta
from typing import Sequence

from sqlalchemy import select, insert, update

from src.infrastructure.models import Chat, DocVersion, DocOrigin, Message
from src.infrastructure.repositories.base import SQLAlchemyRepo

# Import functions from vectordb.py
from src.application.vectordb import initialize_pinecone, search_text, text_to_vector


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
        doc_version = DocVersion(
            content=content, chat_id=chat_id, doc_origin_id=doc_origin_id)
        self._session.add(doc_version)
        await self._session.commit()
        await self._session.refresh(doc_version)
        return doc_version

    async def get_doc_origin_by_id(self, doc_origin_id: str) -> DocOrigin:
        stmt = select(DocOrigin).where(DocOrigin.id == doc_origin_id)
        result = await self._session.execute(stmt)
        return result.scalar()

    async def create_message(self, chat_id: str, content: str, is_user: bool) -> Message:
        message = Message(content=content, chat_id=chat_id, is_user=is_user)
        self._session.add(message)
        await self._session.commit()
        await self._session.refresh(message)
        return message

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

    async def search_doc_in_vectordb(self, text: str) -> Sequence[DocOrigin]:
        index = initialize_pinecone()
        search_results = search_text(text, index)
        doc_origins = []
        for result in search_results:
            doc_origin_id = result['id']
            doc_origin = await self.get_doc_origin_by_id(doc_origin_id)
            if doc_origin:
                doc_origins.append(doc_origin)
        return doc_origins
    
    async def get_user_chats(self, user_id: str) -> list[Chat]:
        stmt = (
            select(Chat)
            .where(Chat.user_id == user_id)
        )
        resp = await self._session.execute(stmt)
        return resp.scalars().all()
