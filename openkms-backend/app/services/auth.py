from typing import Optional
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.crud.user import user as user_crud
from app.schemas.user import UserLogin, UserCreate
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash
)
from app.core.config import get_settings


class AuthService:
    """Authentication business logic service."""

    def __init__(self):
        self.settings = get_settings()

    async def login_user(
        self,
        db: AsyncSession,
        login_data: UserLogin
    ) -> dict:
        """Authenticate user and return JWT tokens."""
        user = await user_crud.authenticate(
            db,
            username=login_data.username,
            password=login_data.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled",
            )

        # Create JWT tokens
        access_token_expires = timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )

        refresh_token = create_refresh_token(data={"sub": user.username})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value
            }
        }

    async def register_user(
        self,
        db: AsyncSession,
        user_data: UserCreate
    ) -> dict:
        """Register a new user."""
        # Check if user already exists
        existing_user = await user_crud.get_by_username(db, username=user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        existing_email = await user_crud.get_by_email(db, email=user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        user = await user_crud.create(db, obj_in=user_data)

        # Create tokens for immediate login
        access_token_expires = timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )

        refresh_token = create_refresh_token(data={"sub": user.username})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value
            },
            "message": "User registered successfully"
        }

    async def refresh_tokens(
        self,
        db: AsyncSession,
        refresh_token: str
    ) -> dict:
        """Refresh access token using refresh token."""
        from app.core.security import verify_refresh_token

        payload = verify_refresh_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user = await user_crud.get_by_username(db, username=username)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new access token
        access_token_expires = timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )

        new_refresh_token = create_refresh_token(data={"sub": user.username})

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    async def change_password(
        self,
        db: AsyncSession,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> dict:
        """Change user password."""
        user = await user_crud.get(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Update password
        user.hashed_password = get_password_hash(new_password)
        await db.commit()
        await db.refresh(user)

        return {"message": "Password changed successfully"}


auth_service = AuthService()