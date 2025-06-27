# app/schemas/email_token.py
from pydantic import BaseModel

class VerifyEmailRequest(BaseModel):
    token: str
