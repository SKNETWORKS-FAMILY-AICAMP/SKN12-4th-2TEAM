# app/schemas/chat.py
from pydantic import BaseModel
from datetime import datetime

class ChatRequest(BaseModel):
    question: str
    chatroom_id: int
    
class ChatResponse(BaseModel):
    id: int
    response: str
    created_at: datetime

class ChatHistoryResponse(BaseModel):
    id: int
    user_id: int
    question: str
    response: str
    created_at: datetime

    class Config:
        orm_mode = True
