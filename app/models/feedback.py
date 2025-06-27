from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chat.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    score = Column(Integer, nullable=False)  # "좋음" 또는 "나쁨"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # 관계 설정 (선택)
    chat = relationship("Chat", back_populates="feedback")   # Chat 모델에서 역방향 설정 필요
    user = relationship("User", back_populates="feedback")   # User 모델에서 역방향 설정 필요