from datetime import datetime
from pydantic import BaseModel, UUID4


class NewChatOut(BaseModel):
    chat_id: UUID4
    doc_version_id: UUID4


class DocVersionOut(BaseModel):
    id: UUID4
    content: str | None
    created_at: datetime
    updated_at: datetime
    

class MessageOut(BaseModel):
    content: str
    is_user: bool
    created_at: datetime

class ChatOut(BaseModel):
    id: UUID4
    title: str | None
    created_at: datetime
    image_url: str
    doc_versions: list[DocVersionOut]
    messages: list[MessageOut]


class NewMessageIn(BaseModel):
    chat_id: UUID4
    content: str

class NewMessageOut(BaseModel):
    content: str
    new_doc_version_id: str | None = None

