from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.models.user import User

from app.api.deps import get_async_db, get_current_user
from app.schemas.user import UserLogin, UserCreate
from app.services.auth import auth_service

router = APIRouter()


@router.post("/login", response_model=dict)
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Authenticate user and return JWT tokens.

    - **username**: User's username
    - **password**: User's password
    """
    return await auth_service.login_user(db, user_login)


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Register a new user.

    - **username**: Unique username (50 chars max)
    - **email**: Valid email address
    - **full_name**: User's full name
    - **password**: Secure password (min 8 chars)
    - **office_location**: Optional office location
    - **department**: Optional department
    """
    return await auth_service.register_user(db, user_data)


@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_token: Annotated[str, Body(..., embed=True)],
    db: AsyncSession = Depends(get_async_db)
):
    """
    Refresh access token using refresh token.

    - **refresh_token**: Valid refresh token
    """
    return await auth_service.refresh_tokens(db, refresh_token)


@router.post("/change-password", response_model=dict)
async def change_password(
    current_password: Annotated[str, Body(...)],
    new_password: Annotated[str, Body(...)],
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change user password.

    - **current_password**: Current password
    - **new_password**: New password (min 8 chars)
    """
    return await auth_service.change_password(
        db, current_user.id, current_password, new_password
    )


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    """
    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "office_location": current_user.office_location,
            "department": current_user.department,
            "role": current_user.role.value,
            "is_active": current_user.is_active
        },
        "message": "User information retrieved successfully"
    }