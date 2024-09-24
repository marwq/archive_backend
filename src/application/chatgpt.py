import json

from openai import AsyncOpenAI
from loguru import logger

from src.application.redis import redis_client
from config import settings


client = AsyncOpenAI(api_key=settings.OPENAI_TOKEN)


async def ocr(fileurl: str, doc_id: str) -> str:
    response = await client.chat.completions.create(
        stream_options={"include_usage": False},
        stream=True,
        model="gpt-4o",
        messages=[
            {
                "role": "assistant",
                "content": """Ты — профессионал в области распознавания текста с изображений. Независимо от того, насколько сложно определить текст на картинке, ты идеально определяешь его. Картинка будет иметь ВСЕГДА иметь текст на русском или казахском. Если же часть текста потеряна, страница порвана, отсутствует слово, то вставляй слова по смыслу или схожие по оставшимся буквам. Твоя задача — преобразовать текст с любого изображения в читаемый формат Markdown, используя определенные правила разметки. Главное - отправь ВЕСЬ видимый текст целиком. Ты должен сделать так, чтобы текст выделял важные элементы. Ты не добавляешь никаких комментариев или лишней информации, только результат распознавания текста в нужном формате. Не используй "\n" для переноса строки, используй Enter.
                Ответ должен быть в формате plaintext и содержать Markdown текст Пример ответа:
                "###Оглавление Пример текста с Markdown разметкой."
                Пользователь же отправляет изображение, на котором изображен текст, который нужно распознать в следующем формате:
                {
                    "image_url": "https://example.com/image.jpg"
                }
            """,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": fileurl,
                        },
                    },
                ],
            }
        ],
    )
    full_text = ""
    async for text in response.response.aiter_lines():
        if not text:
            continue
        data = text.removeprefix("data: ")
        if data.strip() == "[DONE]":
            break
        data = json.loads(text.removeprefix("data: "))
        if data["choices"][0]["finish_reason"]:
            break
        chunk_text = data["choices"][0]["delta"]["content"]
        await redis_client.rpush(f"stream:{doc_id}", chunk_text)
        logger.info(chunk_text)
        full_text += chunk_text
    await redis_client.rpush(f"stream:{doc_id}", "[close]")
    await redis_client.srem("active_streams", doc_id)
    return full_text
