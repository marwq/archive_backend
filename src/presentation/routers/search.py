from typing import Annotated, List
import asyncio
from secrets import token_hex

from fastapi import APIRouter, Form, UploadFile, File, Depends, WebSocket, BackgroundTasks
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool
from pydantic import UUID4
from loguru import logger

from src.infrastructure.uow import SQLAlchemyUoW
from src.application.s3 import upload_s3_and_ocr
from src.application.text_to_pdf import text_to_pdf
from src.presentation.di import get_uow, get_user_id
from ..schemas.search import DocOriginOut, DocVersionIn, SearchOut, SearchIn, DocVersionOut, DocIn, ChatFromSearchIn, ChatFromSearchOut
from config import settings
from src.application.redis import redis_client


router = APIRouter(prefix="/doc", tags=["doc"])


@router.get("/{doc_id}")
async def get_doc(
    doc_id: UUID4,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)] = ...,
) -> DocOriginOut:
    async with uow:
        doc = await uow.chat_repo.get_doc_origin_by_id(str(doc_id))
        doc_origin_out = DocOriginOut(
            id=doc.id,
            is_archive=doc.is_archive,
            content=doc.content,
            created_at=doc.created_at,
            updated_at=doc.updated_at
        )
    return doc_origin_out


@router.post("/search")
async def search_from_vectordb(
    data: SearchIn,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)] = ...,
) -> SearchOut:
    data.text
    async with uow:
        docs = await uow.chat_repo.search_doc_in_vectordb(data.text)
        doc_origins_out = [
            DocOriginOut(
                id=doc.id,
                is_archive=doc.is_archive,
                content=doc.content,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            )
            for doc in docs
        ]
    return SearchOut(doc_origins=doc_origins_out)


@router.post("/markdown-to-pdf")
async def markdown_to_pdf(data: DocIn) -> FileResponse:
    # Convert Markdown to HTML
    filename = f"{token_hex(4)}.pdf"
    filepath = f"temp_files/{filename}"
    await run_in_threadpool(text_to_pdf, data.text, filepath)

    # Return the generated PDF file as a response
    return FileResponse(path=filepath, filename=filename, media_type="application/pdf")


@router.post("/save")
async def save_doc(
    data: DocVersionIn,
    user_id: str = Depends(get_user_id),
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)] = ...,
):
    async with uow:
        doc_version = await uow.chat_repo.edit_doc_version(data.doc_version_id, data.content)
        doc_version_out = dict(
            id=data.doc_version_id,
            content=data.content,
        )
    return doc_version_out


@router.post("/chat_from_search")
async def chat_from_search(
    data: ChatFromSearchIn,
    user_id: Annotated[str, Depends(get_user_id)],
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)] = ...,
) -> ChatFromSearchOut:
    async with uow:
        chat = await uow.chat_repo.create_chat(user_id)
        doc_origin = await uow.chat_repo.get_doc_origin_by_id(data.doc_origin_id)
        doc_version = await uow.chat_repo.create_doc_version(chat.id, data.doc_origin_id, doc_origin.content)
        return ChatFromSearchOut(doc_origin.content, chat.id, doc_version.id)

