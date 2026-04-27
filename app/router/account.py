from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.dependencies.deps import get_db
from app.dependencies.auth import get_current_user
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse, AccountPaginatedResponse
from app.services.account_service import AccountService
from app.models.user import User

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AccountService(db).create_account(account_data, current_user)


@router.get("/", response_model=AccountPaginatedResponse)
def get_accounts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    order: Optional[str] = Query("asc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = {"name": name}
    return AccountService(db).get_accounts(current_user, page, limit, filters, sort_by, order)


# FIX: /summary BEFORE /{account_id} so it isn't swallowed as an ID
@router.get("/summary/{account_id}")
def get_account_summary(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns total income, expense, and net balance for a single account."""
    return AccountService(db).get_account_summary(account_id, current_user)


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AccountService(db).get_account_by_id(account_id, current_user)


@router.patch("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: str,
    update_data: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AccountService(db).update_account(account_id, update_data, current_user)


@router.delete("/{account_id}", response_model=AccountResponse)
def delete_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AccountService(db).delete_account(account_id, current_user)
