from typing import Annotated, List
import asyncio

from fastapi import APIRouter, Form, UploadFile, File, Depends, WebSocket, BackgroundTasks
from fastapi.responses import FileResponse
import markdown
from pydantic import UUID4
from loguru import logger
from weasyprint import HTML

from src.infrastructure.uow import SQLAlchemyUoW
from src.application.s3 import upload_s3_and_ocr
from src.presentation.di import get_uow, get_user_id
from ..schemas.search import DocOriginOut, SearchOut, SearchIn, DocVersionOut, DocIn
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
    html_content = markdown.markdown(data.text)

    # Create an HTML object from the converted HTML content
    html = HTML(string=html_content)

    # Generate the PDF file and save it
    pdf_filename = "output.pdf"
    html.write_pdf(pdf_filename)

    # Return the generated PDF file as a response
    return FileResponse(path=pdf_filename, filename=pdf_filename, media_type="application/pdf")
