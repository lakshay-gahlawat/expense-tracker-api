from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.dependencies.deps import get_db
from app.dependencies.auth import get_current_user
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionPaginatedResponse,
)
from app.services.transaction_service import TransactionService
from app.models.user import User

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    trans_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TransactionService(db).create_transaction(trans_data, current_user)


@router.get("/", response_model=TransactionPaginatedResponse)
def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    account_id: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    from_date: Optional[str] = Query(None, description="ISO format: 2024-01-01"),
    to_date: Optional[str] = Query(None, description="ISO format: 2024-12-31"),
    sort_by: Optional[str] = Query(None),
    order: Optional[str] = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = {
        "transaction_type": transaction_type,
        "category": category,
        "account_id": account_id,
        "min_amount": min_amount,
        "max_amount": max_amount,
        "from_date": from_date,
        "to_date": to_date,
    }
    return TransactionService(db).get_transactions(
        current_user, page, limit, filters, search, sort_by, order
    )


# All named sub-routes BEFORE /{trans_id}
@router.get("/summary")
def get_summary(
    from_date: Optional[str] = Query(None, description="ISO format: 2024-01-01"),
    to_date: Optional[str] = Query(None, description="ISO format: 2024-12-31"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns overall income, expense, and balance. Optionally filter by date range."""
    from_dt = datetime.fromisoformat(from_date) if from_date else None
    to_dt = datetime.fromisoformat(to_date) if to_date else None
    return TransactionService(db).get_summary(current_user, from_dt, to_dt)


@router.get("/categories")
def get_category_breakdown(
    transaction_type: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns income/expense totals grouped by category."""
    from_dt = datetime.fromisoformat(from_date) if from_date else None
    to_dt = datetime.fromisoformat(to_date) if to_date else None
    return TransactionService(db).get_category_breakdown(current_user, transaction_type, from_dt, to_dt)


@router.get("/trends/{year}")
def get_monthly_trends(
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns month-by-month income vs expense for a given year."""
    return TransactionService(db).get_monthly_trends(current_user, year)


@router.get("/{trans_id}", response_model=TransactionResponse)
def get_transaction(
    trans_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TransactionService(db).get_transaction_by_id(trans_id, current_user)


@router.patch("/{trans_id}", response_model=TransactionResponse)
def update_transaction(
    trans_id: str,
    trans_update: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TransactionService(db).update_transaction(trans_id, trans_update, current_user)


@router.delete("/{trans_id}", response_model=TransactionResponse)
def delete_transaction(
    trans_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TransactionService(db).delete_transaction(trans_id, current_user)
