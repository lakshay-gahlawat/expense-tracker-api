from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    created_at: datetime

class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str