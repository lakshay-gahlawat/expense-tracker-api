from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal


class TransactionCreate(BaseModel):
    amount: Decimal
    transaction_type: Literal["income", "expense"]
    account_id: str
    category: str
    description: Optional[str] = None
    date: datetime


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    transaction_type: Optional[Literal["income", "expense"]] = None
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    account_id: str
    amount: Decimal
    transaction_type: Literal["income", "expense"]
    category: str
    description: Optional[str] = None
    date: datetime


class TransactionPaginatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[TransactionResponse]
    total: int
    page: int
    limit: int
    pages: int