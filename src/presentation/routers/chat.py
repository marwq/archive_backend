from typing import Annotated
import asyncio

from fastapi import APIRouter, UploadFile, File, Depends, WebSocket, BackgroundTasks
from pydantic import UUID4
from loguru import logger

from src.infrastructure.uow import SQLAlchemyUoW
from src.application.s3 import upload_s3_and_ocr
from src.presentation.di import get_uow, get_user_id
from ..schemas.chat import NewChatOut, MessageIn, MessageOut
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
        chat = await uow.chat_repo.create_chat(user_id, ext)
        chat_id = chat.id
        doc = await uow.chat_repo.create_doc(chat_id)
        doc_id = doc.id
    await redis_client.sadd("active_streams", str(doc_id))
    background_tasks.add_task(upload_s3_and_ocr, await file.read(), settings.AWS_BUCKET_NAME, f"{chat_id}.{ext}", str(doc_id))
    return NewChatOut(chat_id=chat_id, doc_id=doc_id)

@router.websocket("/streaming/{doc_id}")
async def streaming(
    doc_id: UUID4,
    websocket: WebSocket,
):
    doc_id = str(doc_id)
    logger.info(f"Stream {doc_id}")
    await websocket.accept()
    while True:
        text = "".join(await redis_client.lpop(f"stream:{doc_id}", 100))
        if text:
            await websocket.send_text(text)
            logger.info(f"Stream {doc_id} text: {text}")
        if not redis_client.sismember("acitve_streams", str(doc_id)):
            logger.info(f"Stream {doc_id} leaving")
            break
        await asyncio.sleep(0.3)
    await websocket.send_text("[close]")
    await websocket.close()
    

@router.post("/message")
async def message(
    data: MessageIn
):
    ...