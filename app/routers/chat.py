# app/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse
from app.models.chat import Chat
from app.database import get_db
from app import models, schemas
from app.services.rag_pipeline import run_rag_pipeline
from app.dependencies import get_current_user
from app.models.user import User
from datetime import datetime

router = APIRouter()

# Output: List[ChatHistoryResponse] (pydantic schema)
# [
#   {
#     "id": int,
#     "user_id": int,
#     "question": str,
#     "response": str,
#     "created_at": str (datetime)
#   },
#   ...
# ]
@router.get("/chat/{user_id}", response_model=list[schemas.chat.ChatHistoryResponse])
def get_user_chat_history(user_id: int, db: Session = Depends(get_db)):
    chat_history = (
        db.query(models.chat.Chat)
        .filter(models.chat.Chat.user_id == user_id)
        .order_by(models.chat.Chat.created_at.desc())
        .all()
    )
    if not chat_history:
        raise HTTPException(status_code=404, detail="해당 사용자의 대화 이력이 없습니다.")
    return chat_history

# Output: ChatResponse (pydantic schema)
# {
#   "id": int,
#   "response": str,
#   "created_at": str (datetime)
# }
@router.post("/chat", response_model=schemas.chat.ChatResponse)
def chat_with_bot(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # RAG 응답 생성
    result = run_rag_pipeline(request.question)
    answer = result["answer"]
    relevance = result["relevance"]

    # DB 저장
    new_chat = Chat(
        user_id=current_user.id,
        chatroom_id=request.chatroom_id,  # ← 반드시 추가!
        question=request.question,
        response=answer,
        # relevance_score=relevance,  # relevance 저장을 원한다면 모델에도 컬럼 추가 필요
        created_at=datetime.utcnow()
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    return ChatResponse(
        id=new_chat.id,
        response=new_chat.response,
        created_at=new_chat.created_at
    )