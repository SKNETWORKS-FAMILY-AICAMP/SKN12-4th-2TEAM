from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.email_token import EmailToken
from app.models.user import User
from app.services.email_service import send_verification_email
import secrets
from datetime import datetime, timedelta
from app.schemas.user import RegisterRequest
from pydantic import BaseModel
import random

router = APIRouter()

class EmailRequest(BaseModel):
    email: str

class CodeVerifyRequest(BaseModel):
    email: str
    code: str

# Output: {"message": "인증번호가 이메일로 전송되었습니다."}
@router.post("/send-code")
async def send_code(req: EmailRequest, db: Session = Depends(get_db)):
    email = req.email
    # 6자리 숫자 코드 생성
    code = str(random.randint(100000, 999999))
    # 기존 인증번호 만료 처리
    db.query(EmailToken).filter(
        EmailToken.email == email,
        EmailToken.is_verified == False
    ).update({"expires_at": datetime.utcnow()})
    # 새 인증번호 저장
    email_token = EmailToken(
        email=email,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
        is_verified=False
    )
    db.add(email_token)
    db.commit()
    # 이메일 발송
    await send_verification_email(email, code)
    return {"message": "인증번호가 이메일로 전송되었습니다."}

# Output: {"message": "인증이 완료되었습니다."}
@router.post("/verify-code")
def verify_code(req: CodeVerifyRequest, db: Session = Depends(get_db)):
    email = req.email
    code = req.code
    token = db.query(EmailToken).filter(
        EmailToken.email == email,
        EmailToken.code == code,
        EmailToken.expires_at > datetime.utcnow(),
        EmailToken.is_verified == False
    ).first()
    if not token:
        raise HTTPException(status_code=400, detail="인증번호가 올바르지 않거나 만료되었습니다.")
    token.is_verified = True
    db.commit()
    return {"message": "인증이 완료되었습니다."}

# Output: {"message": "회원가입이 완료되었습니다"}
@router.post("/register-after-verification")
async def register_after_verification(user_data: RegisterRequest, db: Session = Depends(get_db)):
    """이메일 인증 후 회원가입을 처리합니다."""
    # 이메일 중복 확인
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
    try:
        # 이메일 인증 확인
        email_token = db.query(EmailToken).filter(
            EmailToken.email == user_data.email,
            EmailToken.is_verified == True
        ).first()
        if not email_token:
            raise HTTPException(status_code=400, detail="이메일 인증이 필요합니다")
        # 사용자 생성
        from app.utils.security import get_password_hash
        user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            name=user_data.name,
            company=user_data.company,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        # 회원가입 후 토큰에 user_id 연결
        email_token.user_id = user.id
        db.commit()
        return {"message": "회원가입이 완료되었습니다"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"회원가입 실패: {str(e)}")

# Output: {"verified": true}
@router.get("/check-verified")
def check_verified(email: str, db: Session = Depends(get_db)):
    token = db.query(EmailToken).filter(
        EmailToken.email == email,
        EmailToken.is_verified == True
    ).first()
    return {"verified": bool(token)}
