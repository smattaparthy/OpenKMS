from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.models.training import TrainingCategory, TrainingLevel, TrainingStatus


class TrainingFilter(BaseModel):
    """Training filter parameters."""
    search: Optional[str] = None
    category: Optional[TrainingCategory] = None
    level: Optional[TrainingLevel] = None
    location: Optional[str] = None
    status: Optional[TrainingStatus] = None
    start_date_from: Optional[datetime] = None
    start_date_to: Optional[datetime] = None


class TrainingBase(BaseModel):
    """Base training schema."""
    title: str
    description: Optional[str] = None
    category: TrainingCategory
    level: TrainingLevel = TrainingLevel.BEGINNER
    location: str
    max_participants: int = 30
    start_date: datetime
    end_date: datetime
    duration_hours: float
    credits_required: int = 1
    cost: float = 0.0
    instructor: Optional[str] = None
    prerequisites: Optional[str] = None
    learning_objectives: Optional[str] = None


class TrainingCreate(TrainingBase):
    """Training creation schema."""
    pass


class TrainingUpdate(BaseModel):
    """Training update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[TrainingCategory] = None
    level: Optional[TrainingLevel] = None
    status: Optional[TrainingStatus] = None
    location: Optional[str] = None
    max_participants: Optional[int] = None
    duration_hours: Optional[float] = None
    credits_required: Optional[int] = None
    cost: Optional[float] = None
    instructor: Optional[str] = None
    prerequisites: Optional[str] = None
    learning_objectives: Optional[str] = None


class TrainingInDBBase(TrainingBase):
    """Base training schema with database fields."""
    id: int
    status: TrainingStatus
    current_participants: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Training(TrainingInDBBase):
    """Training response schema."""
    creator_name: Optional[str] = None
    available_spots: Optional[int] = None


class TrainingList(BaseModel):
    """Training list response schema."""
    trainings: List[Training]
    total: int
    page: int
    size: int