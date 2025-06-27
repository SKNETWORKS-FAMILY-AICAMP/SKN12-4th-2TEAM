from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

# 환경에 따른 데이터베이스 URL 설정
def get_database_url():
    # 환경변수에서 DATABASE_URL을 가져오거나 기본값 사용
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        return database_url
    
    # 로컬 개발 환경을 위한 기본값
    return "postgresql://esgadmin:mysecretpassword@localhost:5432/esg_chatbot"

DATABASE_URL = get_database_url()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# FastAPI 의존성으로 사용할 DB 세션 함수
def get_db():
    from sqlalchemy.orm import Session
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()