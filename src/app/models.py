from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    username: str
    language_code: str

class Chat(BaseModel):
    id: int
    first_name: str
    username: str
    type: str

class Message(BaseModel):
    message_id: int
    user: User = Field(alias="from")
    chat: Chat
    date: int
    text: str

class Update(BaseModel):
    update_id: int
    message: Optional[Message] = None

    