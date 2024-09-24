from datetime import datetime
from pydantic import BaseModel, UUID4


class SearchIn(BaseModel):
    text: str


class DocVersionOut(BaseModel):
    id: UUID4
    content: str
    created_at: datetime
    updated_at: datetime


class SearchOut(BaseModel):
    doc_versions: list[DocVersionOut]
