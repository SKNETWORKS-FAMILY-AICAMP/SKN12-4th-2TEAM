# app/routers/auth.py
from fastapi import APIRouter, HTTPException, Depends, Response, Body
from sqlalchemy.orm import Session
from app.dependencies import get_current_user
from app.schemas.user import RegisterRequest, LoginRequest, FindEmailRequest, PasswordResetRequest, PasswordResetCodeVerifyRequest, PasswordResetFinalRequest, UserOut
from app.schemas.email_token import VerifyEmailRequest
from app.models.user import User
from app.models.email_token import EmailToken
from app.database import get_db
from app.utils.security import hash_password, generate_token, verify_password
from app.services.email_service import send_verification_email
from datetime import datetime, timedelta
from pydantic import BaseModel
import random

router = APIRouter()

# Output: {"message": "회원가입이 완료되었습니다. 이메일 인증을 진행해주세요."}
@router.post("/register")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    hashed_pw = hash_password(request.password)
    new_user = User(
        email=request.email,
        password_hash=hashed_pw,
        name=request.name,
        company=request.company
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = generate_token()
    token_entry = EmailToken(user_id=new_user.id, token=token)
    db.add(token_entry)
    db.commit()

    send_verification_email(to_email=new_user.email, token=token)

    return {"message": "회원가입이 완료되었습니다. 이메일 인증을 진행해주세요."}


# Output: {"message": "이메일 인증이 완료되었습니다."}
@router.post("/verify-email")
def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    token_entry = db.query(EmailToken).filter(EmailToken.token == request.token).first()

    if not token_entry:
        raise HTTPException(status_code=404, detail="토큰이 유효하지 않습니다.")
    if token_entry.is_used:
        raise HTTPException(status_code=400, detail="이미 사용된 토큰입니다.")
    if token_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="토큰이 만료되었습니다.")

    user = db.query(User).filter(User.id == token_entry.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")

    user.is_verified = True
    token_entry.is_used = True
    db.commit()

    return {"message": "이메일 인증이 완료되었습니다."}


# Output: {"message": "로그인 성공", "user_id": 1}
@router.post("/login")
def login_user(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="이메일 인증이 완료되지 않았습니다.")

    response.set_cookie(key="user_id", value=str(user.id))
    return {"message": "로그인 성공", "user_id": user.id}


# Output: {"message": "로그아웃 되었습니다."}
@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie(key="user_id")
    return {"message": "로그아웃 되었습니다."}

# Output: {"message": "비밀번호가 성공적으로 변경되었습니다."}
@router.post("/change-password")
def change_password(
    current_password: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="현재 비밀번호가 올바르지 않습니다.")
    if verify_password(new_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="새 비밀번호가 기존 비밀번호와 동일합니다.")
    current_user.password_hash = hash_password(new_password)
    db.commit()
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}
    
# --- 아이디(이메일) 찾기 ---
# Output: {"email": "abc****@naver.com"}
@router.post("/find-email")
def find_email(req: FindEmailRequest, db: Session = Depends(get_db)):
    # 회사명은 company_id로 고정값 매핑 필요 (여기선 1로 가정)
    user = db.query(User).filter(User.name == req.name, User.company == req.company_name).first()
    if not user:
        raise HTTPException(status_code=404, detail="일치하는 사용자를 찾을 수 없습니다.")
    # 이메일 마스킹 (ex: kwo****@naver.com)
    email = user.email
    masked = email
    if "@" in email:
        local, domain = email.split("@", 1)
        if len(local) > 3:
            masked = local[:3] + "*" * (len(local)-3) + "@" + domain
        else:
            masked = local[0] + "*" * (len(local)-1) + "@" + domain
    return {"email": masked}

# --- 비밀번호 재설정 인증번호 발송 ---
# Output: {"message": "인증번호가 이메일로 전송되었습니다."}
@router.post("/request-password-reset")
async def request_password_reset(req: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="가입된 이메일이 없습니다.")
    code = str(random.randint(100000, 999999))
    # 기존 인증번호 만료 처리
    db.query(EmailToken).filter(
        EmailToken.email == req.email,
        EmailToken.is_verified == False
    ).update({"expires_at": datetime.utcnow()})
    # 새 인증번호 저장
    email_token = EmailToken(
        email=req.email,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
        is_verified=False
    )
    db.add(email_token)
    db.commit()
    # 이메일 발송 (await 사용)
    await send_verification_email(req.email, code)
    return {"message": "인증번호가 이메일로 전송되었습니다."}

# --- 비밀번호 재설정 인증번호 확인 ---
# Output: {"message": "인증이 완료되었습니다."}
@router.post("/verify-password-reset-code")
def verify_password_reset_code(req: PasswordResetCodeVerifyRequest, db: Session = Depends(get_db)):
    token = db.query(EmailToken).filter(
        EmailToken.email == req.email,
        EmailToken.code == req.code,
        EmailToken.expires_at > datetime.utcnow(),
        EmailToken.is_verified == False
    ).first()
    if not token:
        raise HTTPException(status_code=400, detail="인증번호가 올바르지 않거나 만료되었습니다.")
    token.is_verified = True
    db.commit()
    return {"message": "인증이 완료되었습니다."}

# --- 비밀번호 재설정 ---
# Output: {"message": "비밀번호가 재설정되었습니다."}
@router.post("/reset-password")
def reset_password(req: PasswordResetFinalRequest, db: Session = Depends(get_db)):
    # 인증번호 확인
    token = db.query(EmailToken).filter(
        EmailToken.email == req.email,
        EmailToken.code == req.code,
        EmailToken.is_verified == True
    ).order_by(EmailToken.created_at.desc()).first()
    if not token:
        raise HTTPException(status_code=400, detail="인증이 완료된 코드가 아닙니다.")
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="가입된 이메일이 없습니다.")
    user.password_hash = hash_password(req.new_password)
    db.commit()
    return {"message": "비밀번호가 재설정되었습니다."}


# Output: UserOut (pydantic schema)
@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user