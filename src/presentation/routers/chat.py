from typing import Annotated

from fastapi import APIRouter, UploadFile, File, Depends

from src.infrastructure.uow import SQLAlchemyUoW
from src.application.s3 import upload_file_to_s3
from src.presentation.di import get_uow, get_user_id
from ..schemas.chat import NewChatOut, MessageIn, MessageOut
from config import settings

router = APIRouter(prefix="/chat", tags=["chat"])



@router.post("/new")
async def new(
    file: UploadFile = File(...),
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)] = ...,
    user_id: Annotated[int, Depends(get_user_id)] = ...,
) -> NewChatOut:
    ext = file.filename.rsplit('.', 1)[1]
    async with uow:
        chat = await uow.chat_repo.create_chat(user_id, ext)
        chat_id = chat.id
    await upload_file_to_s3(await file.read(), settings.AWS_BUCKET_NAME, f"{chat_id}.{ext}")
    return NewChatOut(chat_id=chat_id, stream_id=chat_id)
    

@router.post("/message")
async def message(
    data: MessageIn
):
    ...