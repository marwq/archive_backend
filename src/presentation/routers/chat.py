from typing import Annotated
from itertools import chain
import asyncio

from fastapi import APIRouter, UploadFile, File, Depends, WebSocket, BackgroundTasks
from pydantic import UUID4
from loguru import logger

from src.infrastructure.uow import SQLAlchemyUoW
from src.infrastructure.models import Chat, DocOrigin, DocVersion
from src.application.s3 import upload_s3_and_ocr, get_download_link_from_s3_cached
from src.presentation.di import get_uow, get_user_id
from ..schemas.chat import NewChatOut, NewMessageIn, NewMessageOut, ChatOut, DocVersionOut, MessageOut
from config import settings
from src.application.redis import redis_client
from src.application.chatgpt import generate_answer, rewrite_doc

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
        message = await uow.chat_repo.create_message(chat_id, "Если есть вопросы или нужно ввести правки напишите сюда запрос", False)
        doc_origin = await uow.chat_repo.create_doc_origin(False, ext=ext)
        doc_origin_id = doc_origin.id
        doc_version = await uow.chat_repo.create_doc_version(chat_id, doc_origin_id)
        doc_version_id = doc_version.id
    await redis_client.sadd("active_streams", str(doc_version_id))
    background_tasks.add_task(upload_s3_and_ocr, await file.read(), settings.AWS_BUCKET_NAME, f"{doc_origin_id}.{ext}", str(doc_version_id))
    return NewChatOut(chat_id=chat_id, doc_version_id=doc_version_id)


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
    data: NewMessageIn,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)] = ...,
    background_tasks: BackgroundTasks = ...,
) -> NewMessageOut:
    chat_id = str(data.chat_id)
    async with uow:
        chat = await uow.chat_repo.get_item_by_id(chat_id)
        doc_origin = chat.doc_versions[0].doc_origin
        origin_content = doc_origin.content
        user_message = await uow.chat_repo.create_message(chat_id, data.content, True)
        messages = [
            {
                "role": "system",
                "content": "Твой чат начался с того что ты распознал текст из архивной картинки. Теперь твоя задача отвечать на вопросы по документу коротко и ясно.\n"
                "Если вопрос подразумевает переписание документа то используй функцию \"rewrite_doc\". \n" +
                "Функция \"rewrite_doc\" не принимает аргументов,  она лишь говорит бекенду что нужно вызвать другой ИИ для переписания.\n" +
                "То есть если задали вопрос то просто отвечаешь на него, если попросили переписать каким то образом, то отвечаешь в роде \"Хорошо, переписываю ваш документ\" и вызываешь функцию \"rewrite_doc\".",
            },
            {
                "role": "assistant",
                "content": origin_content
            }
        ] + [
            {
                "role": "user" if message.is_user else "assistant",
                "content": message.content
            }
            for message in chain(chat.messages, [user_message])
        ]
        content, rewrite_requested = await generate_answer(messages)
        await uow.chat_repo.create_message(chat_id, content, False)
        if rewrite_requested:
            new_doc_version = await uow.chat_repo.create_doc_version(chat_id, doc_origin.id)
            new_doc_version_id = str(new_doc_version.id)
        else:
            new_doc_version_id = None

    if rewrite_requested:
        background_tasks.add_task(
            rewrite_doc, origin_content, data.content, new_doc_version_id)

    return NewMessageOut(content=content, new_doc_version_id=new_doc_version_id)


@router.get("/list")
async def chat_list(
    user_id: Annotated[int, Depends(get_user_id)],
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
) -> list[ChatOut]:
    resp = []
    async with uow:
        for chat in await uow.chat_repo.get_user_chats(user_id):
            doc_origin = chat.doc_versions[0].doc_origin
            object_name = f"{doc_origin.id}.{doc_origin.ext}"
            image_url = await get_download_link_from_s3_cached(settings.AWS_BUCKET_NAME, object_name)
            chat_out = ChatOut(
                id=chat.id,
                title=chat.title,
                created_at=chat.created_at,
                image_url=image_url,
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
                    MessageOut(
                        id=msg.id,
                        is_user=msg.is_user,
                        content=msg.content,
                        created_at=msg.created_at,
                    )
                    for msg in chat.messages
                ]
            )
            resp.append(chat_out)
    return resp


@router.get("/{chat_id}")
async def get_chat(
    chat_id: UUID4,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)] = ...,
) -> ChatOut:
    async with uow:
        chat = await uow.chat_repo.get_item_by_id(str(chat_id))
        doc_origin = chat.doc_versions[0].doc_origin
        object_name = f"{doc_origin.id}.{doc_origin.ext}"
        image_url = await get_download_link_from_s3_cached(settings.AWS_BUCKET_NAME, object_name)
        resp = ChatOut(
            id=chat.id,
            title=chat.title,
            created_at=chat.created_at,
            image_url=image_url,
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
                MessageOut(
                    id=msg.id,
                    is_user=msg.is_user,
                    content=msg.content,
                    created_at=msg.created_at,
                )
                for msg in chat.messages
            ]
        )
    return resp