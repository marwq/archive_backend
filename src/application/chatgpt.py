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
            "content": "Recognize the text from the image and format it in Markdown. Wrap any found dates in the <date></date> tag and phone numbers in the <phone></phone> tag. Maintain proper Markdown formatting (e.g., #, ## for headers). Reply with only the recognized and formatted text without any comments.",
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
    