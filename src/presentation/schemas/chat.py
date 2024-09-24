from pydantic import BaseModel, UUID4


class NewChatOut(BaseModel):
    chat_id: UUID4
    stream_id: UUID4

class MessageIn(BaseModel):
    content: str
    chat_id: UUID4

class MessageOut(BaseModel):
    ...
