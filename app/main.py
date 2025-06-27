from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app import database
from app.database import engine
from app.routers import chat, feedback, auth, email, chat_room
from dotenv import load_dotenv
import os
import app.models  # 모든 모델 import

load_dotenv()  # .env 파일 로드

app = FastAPI()

# CORS 설정 (프론트엔드와의 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000", 
        "http://localhost:5500", 
        "http://localhost:3000",
        "http://54.180.86.31",
        "http://54.180.86.31:80",
        "http://54.180.86.31:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="frontend/assets"), name="static")
app.mount("/common", StaticFiles(directory="frontend/common"), name="common")

# 프론트엔드 HTML 파일들 서빙
@app.get("/")
async def serve_index():
    return FileResponse("frontend/index.html")

@app.get("/login")
async def serve_login():
    return FileResponse("frontend/login.html")

@app.get("/register")
async def serve_register():
    return FileResponse("frontend/register.html")

@app.get("/find_account")
async def serve_find_account():
    return FileResponse("frontend/find_account.html")

@app.get("/chatbot")
async def serve_chatbot():
    return FileResponse("frontend/chatbot.html")

@app.get("/mypage")
async def serve_mypage():
    return FileResponse("frontend/mypage.html")

# API 라우터들
app.include_router(auth.router, prefix="/auth", tags=["Auth"])        # 회원가입, 로그인, 로그아웃
app.include_router(chat.router, prefix='/chat',tags=["Chat"])         # 챗봇 질문/기록 조회
app.include_router(feedback.router, prefix='/feedback', tags=["Feedback"]) # 피드백 제출
app.include_router(email.router, prefix="/email", tags=["Email"]) # 이메일 인증
app.include_router(chat_room.router, prefix="/chatroom", tags=["ChatRoom"])

# DB 테이블 생성
database.Base.metadata.create_all(bind=engine)

