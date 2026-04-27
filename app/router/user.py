from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.deps import get_db
from app.dependencies.auth import get_current_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin, TokenResponse
from app.services.user_service import UserService
from app.core.auth import create_access_token
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return UserService(db).create_user(user_data)


# FIX: /login MUST be above /{user_id} — otherwise "login" is treated as a user_id
@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = UserService(db).authenticate_user(credentials.email, credentials.password)
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return UserService(db).get_user_by_id(user_id, current_user)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return UserService(db).update_user(user_id, user_update, current_user)


@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return UserService(db).delete_user(user_id, current_user)
