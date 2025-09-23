from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    username: str
    email: EmailStr
    full_name: str
    office_location: Optional[str] = None
    department: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserUpdate(BaseModel):
    """User update schema."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    office_location: Optional[str] = None
    department: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    """Base user schema with database fields."""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """User response schema."""
    pass


class UserInDB(UserInDBBase):
    """User schema with password hash (for internal use)."""
    hashed_password: str


class UserLogin(BaseModel):
    """User login schema."""
    username: str
    password: str


class Token(BaseModel):
    """JWT token schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload schema."""
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None