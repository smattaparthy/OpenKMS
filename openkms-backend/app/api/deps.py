from typing import Optional, Generator
from fastapi import Depends, HTTPException, status, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db as get_session
from app.core.security import verify_token
from app.crud.user import user as user_crud
from app.models.user import User
from app.core.config import get_settings

# Security
security = HTTPBearer()

settings = get_settings()


async def get_current_user(
    db: AsyncSession = Depends(get_session),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    current_user = await user_crud.get_by_username(db, username=username)
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user (redundant with above but explicit)."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current admin user."""
    from app.models.user import UserRole

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_session)
) -> Optional[User]:
    """Get user if token is provided, otherwise return None."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    try:
        token = auth_header.split(" ")[1]
        payload = verify_token(token)

        if payload is None:
            return None

        username: str = payload.get("sub")
        if username is None:
            return None

        current_user = await user_crud.get_by_username(db, username=username)
        if current_user is None or not current_user.is_active:
            return None

        return current_user
    except Exception:
        return None


# Database dependency alias for clarity
get_async_db = get_session