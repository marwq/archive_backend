from typing import Annotated
import asyncio

from fastapi import APIRouter, UploadFile, File, Depends, WebSocket, BackgroundTasks
from pydantic import UUID4
from loguru import logger

from src.infrastructure.uow import SQLAlchemyUoW
from src.application.s3 import upload_s3_and_ocr
from src.presentation.di import get_uow, get_user_id
from ..schemas.chat import NewChatOut, NewMessageIn, NewMessageOut, ChatOut, DocVersionOut, MessageOut
from config import settings
from src.application.redis import redis_client

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/new")
async def new(
    file: UploadFile = File(...),
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)] = ...,
    user_id: Annotated[int, Depends(get_user_id)] = ...,
    background_tasks: BackgroundTasks = ...,
) -> NewChatOut:
    ext = file.filename.rsplit('.', 1)[1]
    async with uow:
        chat = await uow.chat_repo.create_chat(user_id)
        chat_id = chat.id
        doc_origin = await uow.chat_repo.create_doc_origin(False, ext=ext)
        doc_origin_id = doc_origin.id
        doc_version = await uow.chat_repo.create_doc_version(chat_id, doc_origin_id)
        doc_version_id = doc_version.id
    await redis_client.sadd("active_streams", str(doc_version_id))
    background_tasks.add_task(upload_s3_and_ocr, await file.read(), settings.AWS_BUCKET_NAME, f"{doc_origin_id}.{ext}", str(doc_version_id))
    return NewChatOut(chat_id=chat_id, doc_version_id=doc_version_id)


@router.get("/{chat_id}")
async def get_chat(
    chat_id: UUID4,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)] = ...,
) -> ChatOut:
    async with uow:
        chat = await uow.chat_repo.get_item_by_id(str(chat_id))
        resp = ChatOut(
            id=chat.id,
            title=chat.title,
            created_at=chat.created_at,
            doc_versions=[
                DocVersionOut(
                    id=dv.id,
                    content=dv.content,
                    created_at=dv.created_at,
                    updated_at=dv.updated_at
                )
                for dv in chat.doc_versions
            ],
            messages=[

            ]
        )
    return resp


@router.websocket("/streaming/{doc_version_id}")
async def streaming(
    doc_version_id: UUID4,
    websocket: WebSocket,
):
    doc_version_id = str(doc_version_id)
    logger.info(f"Stream {doc_version_id}")
    await websocket.accept()
    while True:
        data = await redis_client.lpop(f"stream:{doc_version_id}", 100)
        text = ""
        if data:
            text = "".join(data)
        if text:
            await websocket.send_text(text)
            logger.info(f"Stream {doc_version_id} text: {text}")
        if not redis_client.sismember("acitve_streams", str(doc_version_id)):
            logger.info(f"Stream {doc_version_id} leaving")
            break
        await asyncio.sleep(0.3)
    await websocket.send_text("[close]")
    await websocket.close()


@router.post("/message")
async def message(
    data: NewMessageIn
) -> NewMessageOut:
    ...
