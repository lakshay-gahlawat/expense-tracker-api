from app.models.user import User
from fastapi import HTTPException, status
from app.core.security import hash_password, verify_password


class UserService:
    def __init__(self, db):
        self.db = db

    def create_user(self, user_data):
        existing = self.db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )
        user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_users(self, current_user):
        return [current_user]

    def get_user_by_id(self, user_id, current_user):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        return user

    def update_user(self, user_id, user_update, current_user):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        user_data = user_update.model_dump(exclude_unset=True)

        if "email" in user_data:
            conflict = self.db.query(User).filter(
                User.email == user_data["email"],
                User.id != user_id,
            ).first()
            if conflict:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        if "password" in user_data:
            user_data["hashed_password"] = hash_password(user_data.pop("password"))

        for key, value in user_data.items():
            setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id, current_user):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        self.db.delete(user)
        self.db.commit()
        return user

    def authenticate_user(self, email, password):
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        return user
