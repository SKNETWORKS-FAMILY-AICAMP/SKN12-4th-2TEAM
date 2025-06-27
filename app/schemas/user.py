# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    company: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    company: str
    is_verified: bool
    is_admin: bool  # ← 관리자 여부도 응답에 포함 (권한 기반 UI에 필요)
    
    class Config:
        from_attributes = True

class FindEmailRequest(BaseModel):
    name: str
    company_name: str

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetCodeVerifyRequest(BaseModel):
    email: str
    code: str

class PasswordResetFinalRequest(BaseModel):
    email: str
    code: str
    new_password: str