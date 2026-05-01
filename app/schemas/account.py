from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class AccountCreate(BaseModel):
    name: str


class AccountUpdate(BaseModel):
    name: Optional[str] = None


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    user_id: str
    created_at: datetime


class AccountPaginatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[AccountResponse]
    total: int
    page: int
    limit: int
    pages: int