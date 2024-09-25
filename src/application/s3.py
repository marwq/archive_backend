import aioboto3
from loguru import logger
from aiofiles import open as aopen
from starlette.concurrency import run_in_threadpool

from .chatgpt import ocr, generate_title
from .redis import redis_client
# from src.application.upscale import preprocess_image
from src.application.vectordb import text_to_vector, Doc
from src.infrastructure.uow import SQLAlchemyUoW
from src.presentation.di import get_uow
from config import settings


session = aioboto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_DEFAULT_REGION
)


async def upload_s3_and_ocr(
    file_content: bytes,
    bucket_name: str,
    object_name: str,
    doc_version_id: str
) -> None:
    await upload_file_to_s3(file_content, bucket_name, object_name)
    url = await get_download_link_from_s3(bucket_name, object_name)
    logger.info(f"Url: {url}")
    text = await ocr(url, doc_version_id)
    logger.info(text)
    uow = await get_uow()
    async with uow:
        doc_version = await uow.chat_repo.edit_doc_version(doc_version_id, text)
        await uow.chat_repo.edit_doc_origin(doc_version.doc_origin_id, text)
        title = await generate_title(text)
        logger.info(f"Title generated: {title}")
        chat = doc_version.chat
        chat.title = title
        await uow.commit()
    await run_in_threadpool(text_to_vector, Doc(text, doc_version_id))


async def upload_file_to_s3(file_content: bytes, bucket_name: str, object_name: str):
    file_path = f'temp_files/{object_name}'
    # await run_in_threadpool(preprocess_image, file_path, file_path)
    async with aopen(file_path, 'wb') as f:
        await f.write(file_content)

    async with session.client('s3') as s3_client:
        try:
            async with aopen(file_path, 'rb') as file:
                await s3_client.upload_fileobj(file, bucket_name, object_name)
            logger.info(f"File {file_path} uploaded to {bucket_name}/{object_name}")
        except Exception as e:
            logger.info(f"Error uploading file: {e}")
            return False
    return True


async def get_download_link_from_s3(bucket_name: str, object_name: str, expiration: int = 3600):
    """Получить временную ссылку для скачивания файла из S3.

    Args:
        bucket_name (str): Название S3-бакета.
        object_name (str): Имя объекта в бакете.
        expiration (int, optional): Время действия ссылки в секундах (по умолчанию 1 час).

    Returns:
        str: Временная ссылка для скачивания файла.
    """
    async with session.client('s3') as s3_client:
        try:
            download_url = await s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            logger.info(f"Generated download link for {bucket_name}/{object_name}: {download_url}")
            return download_url
        except Exception as e:
            logger.error(f"Error generating download link: {e}")
            return None


async def get_download_link_from_s3_cached(bucket_name: str, object_name: str, expire: int = 3600) -> str:
    url = await redis_client.get(f"download_url:{bucket_name}:{object_name}")
    logger.info(f"url1: {url!r}")
    if not url:
        url = str(await get_download_link_from_s3(bucket_name, object_name, expire))
        logger.info(f"url2: {url!r}")
        await redis_client.set(f"download_url:{bucket_name}:{object_name}", url, expire)
    return url
