from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatRoomCreate(BaseModel):
    title: str

class ChatRoomOut(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    id: int
    chatroom_id: int
    user_id: int
    question: str
    response: str
    created_at: datetime
    feedback_given: bool

    class Config:
        from_attributes = True