from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.models.registration import RegistrationStatus


class RegistrationCreate(BaseModel):
    """Registration creation schema."""
    training_id: int
    notes: Optional[str] = None
    special_requirements: Optional[str] = None


class RegistrationUpdate(BaseModel):
    """Registration update schema."""
    status: Optional[RegistrationStatus] = None
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None


class RegistrationInDBBase(BaseModel):
    """Base registration schema with database fields."""
    id: int
    user_id: int
    training_id: int
    status: RegistrationStatus
    registration_date: datetime
    confirmed_date: Optional[datetime] = None
    cancelled_date: Optional[datetime] = None
    notes: Optional[str] = None
    special_requirements: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Registration(RegistrationInDBBase):
    """Registration response schema."""
    training_title: Optional[str] = None
    user_name: Optional[str] = None
    office_location: Optional[str] = None
    trainer_name: Optional[str] = None


class RegistrationList(BaseModel):
    """Registration list response schema."""
    registrations: List[Registration]
    total: int
    page: int
    size: int


class ConflictResponse(BaseModel):
    """Conflict detection response schema."""
    has_conflicts: bool
    conflicts: list[dict]


class RegistrationResponse(BaseModel):
    """Registration action response schema."""
    status: str
    registration_id: int
    message: str
    conflicts: Optional[list[dict]] = None