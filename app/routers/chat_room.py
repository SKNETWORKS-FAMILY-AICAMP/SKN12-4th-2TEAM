from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.chat_room import ChatRoom
from app.models.chat import Chat
from app.schemas.chat_room import ChatRoomCreate, ChatRoomOut, ChatHistoryResponse
from app.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from typing import List
from datetime import datetime
from app.models.feedback import Feedback

router = APIRouter()

# Output: ChatRoomOut (pydantic schema)
# {
#   "id": int,
#   "user_id": int,
#   "title": str,
#   "created_at": str (datetime)
# }
@router.post("/", response_model=ChatRoomOut)
def create_chat_room(
    req: ChatRoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_room = ChatRoom(
        user_id=current_user.id,
        title=req.title,
        created_at=datetime.utcnow()
    )
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room

# Output: List[ChatRoomOut] (pydantic schema)
# [
#   {
#     "id": int,
#     "user_id": int,
#     "title": str,
#     "created_at": str (datetime)
#   },
#   ...
# ]
@router.get("/list", response_model=List[ChatRoomOut])
def list_my_chat_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rooms = db.query(ChatRoom).filter(ChatRoom.user_id == current_user.id).order_by(ChatRoom.created_at.desc()).all()
    return rooms

# Output: ChatRoomOut (pydantic schema)
# {
#   "id": int,
#   "user_id": int,
#   "title": str,
#   "created_at": str (datetime)
# }
@router.get("/{room_id}", response_model=ChatRoomOut)
def get_chat_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id, ChatRoom.user_id == current_user.id).first()
    if not room:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다.")
    return room

# Output: List[ChatHistoryResponse] (pydantic schema)
# [
#   {
#     "id": int,
#     "chatroom_id": int,
#     "user_id": int,
#     "question": str,
#     "response": str,
#     "created_at": str (datetime),
#     "feedback_given": bool
#   },
#   ...
# ]
@router.get("/{room_id}/messages", response_model=List[ChatHistoryResponse])
def get_chatroom_messages(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    messages = (
        db.query(Chat)
        .filter(Chat.chatroom_id == room_id, Chat.user_id == current_user.id)
        .order_by(Chat.created_at)
        .all()
    )
    result = []
    for msg in messages:
        feedback_exists = db.query(Feedback).filter(
            Feedback.chat_id == msg.id,
            Feedback.user_id == current_user.id
        ).first() is not None
        result.append({
            "id": msg.id,
            "chatroom_id": msg.chatroom_id,
            "user_id": msg.user_id,
            "question": msg.question,
            "response": msg.response,
            "created_at": msg.created_at,
            "feedback_given": feedback_exists
        })
    return result