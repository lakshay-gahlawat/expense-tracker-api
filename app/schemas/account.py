from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AccountCreate(BaseModel):
    name: str


class AccountUpdate(BaseModel):
    name: Optional[str] = None


class AccountResponse(BaseModel):
    id: str
    name: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AccountPaginatedResponse(BaseModel):
    items: list[AccountResponse]
    total: int
    page: int
    limit: int
    pages: int

    class Config:
        from_attributes = True
