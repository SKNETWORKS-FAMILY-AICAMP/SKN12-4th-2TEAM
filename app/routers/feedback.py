from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter()

# Output: FeedbackResponse (pydantic schema)
# {
#   "id": int,
#   "chat_id": int,
#   "score": int,
#   "created_at": str (datetime)
# }
@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db), current_user: models.user.User = Depends(get_current_user)):
    # 존재하는 chat_id인지 확인
    chat = db.query(models.chat.Chat).filter(models.chat.Chat.id == feedback.chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="해당 chat_id의 대화가 존재하지 않습니다.")

    # 2. 중복 피드백 확인 (같은 유저가 같은 chat_id에)
    duplicate = db.query(models.feedback.Feedback).filter(
        models.feedback.Feedback.chat_id == feedback.chat_id,
        models.feedback.Feedback.user_id == current_user.id
    ).first()

    if duplicate:
        raise HTTPException(status_code=400, detail="이미 피드백을 남긴 대화입니다.")
    # 피드백 생성
    feedback_obj = models.feedback.Feedback(
                    chat_id=feedback.chat_id,
                    score=feedback.score,
                    user_id=current_user.id
                    )
    db.add(feedback_obj)
    db.commit()
    db.refresh(feedback_obj)
    return feedback_obj

# Output: List[FeedbackResponse] (pydantic schema)
# [
#   {
#     "id": int,
#     "chat_id": int,
#     "score": int,
#     "created_at": str (datetime)
#   },
#   ...
# ]
@router.get("/feedback/all", response_model=list[FeedbackResponse])
def get_all_feedbacks(
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="관리자만 접근 가능합니다.")

    feedbacks = (
        db.query(models.feedback.Feedback)
        .order_by(models.feedback.Feedback.created_at.desc())
        .all()
    )
    return feedbacks