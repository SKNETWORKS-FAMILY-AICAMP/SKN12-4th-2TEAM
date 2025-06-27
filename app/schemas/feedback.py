from pydantic import BaseModel
from datetime import datetime

class FeedbackCreate(BaseModel):
    chat_id: int
    score: int  # "좋음" 또는 "나쁨"

class FeedbackResponse(BaseModel):
    id: int
    chat_id: int
    score: int
    created_at: datetime

    class Config:
        orm_mode = True
