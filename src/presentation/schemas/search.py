from datetime import datetime
from pydantic import BaseModel, UUID4


class SearchIn(BaseModel):
    text: str


class DocIn(BaseModel):
    text: str


class DocVersionOut(BaseModel):
    id: UUID4
    content: str
    created_at: datetime
    updated_at: datetime


class DocVersionIn(BaseModel):
    doc_version_id: UUID4
    content: str


class DocOriginOut(BaseModel):
    id: UUID4
    content: str
    is_archive: bool
    created_at: datetime
    updated_at: datetime


class SearchOut(BaseModel):
    doc_origins: list[DocOriginOut]


class SaveIn(BaseModel):
    doc_version_id: str


class ChatFromSearchIn(BaseModel):
    doc_origin_id: str

class ChatFromSearchOut(BaseModel):
    content: str
    chat_id: str
    doc_version_id: str
