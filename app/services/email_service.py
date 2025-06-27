# app/services/email_service.py
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import os

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME="ESG Chatbot",
    USE_CREDENTIALS = True
)

def send_verification_email(to_email: EmailStr, code: str):
    try:
        message = MessageSchema(
            subject="[ESG 챗봇] 이메일 인증번호 안내",
            recipients=[to_email],
            body=f"아래 인증번호를 입력하여 이메일 인증을 완료해주세요.\n\n인증번호: {code}\n\n인증번호는 10분간 유효합니다.",
            subtype="plain"
        )
        fm = FastMail(conf)
        return fm.send_message(message)
    except Exception as e:
        # 필요 시 로깅 추가
        raise RuntimeError("이메일 전송 실패: " + str(e))

