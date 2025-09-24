from sqlalchemy import Column, Integer, String, Text, DateTime, Integer, Float, Enum, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum as PyEnum
import uuid


class TrainingCategory(PyEnum):
    TECHNICAL = "technical"
    SOFT_SKILLS = "soft_skills"
    COMPLIANCE = "compliance"
    LEADERSHIP = "leadership"
    SAFETY = "safety"


class TrainingLevel(PyEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class TrainingStatus(PyEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Training(Base):
    """Training model for OpenKMS."""

    __tablename__ = "trainings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(Enum(TrainingCategory), nullable=False)
    level = Column(Enum(TrainingLevel), default=TrainingLevel.BEGINNER, nullable=False)
    status = Column(Enum(TrainingStatus), default=TrainingStatus.DRAFT, nullable=False)

    # Logistics
    location = Column(String(100), nullable=False, index=True)
    max_participants = Column(Integer, default=30, nullable=False)
    current_participants = Column(Integer, default=0, nullable=False)

    # Timing
    start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    end_date = Column(DateTime(timezone=True), nullable=False)
    duration_hours = Column(Float, nullable=False)

    # Pricing and credits
    credits_required = Column(Integer, default=1, nullable=False)
    cost = Column(Float, default=0.0, nullable=False)

    # Metadata
    instructor = Column(String(100), nullable=True)
    prerequisites = Column(Text, nullable=True)
    learning_objectives = Column(Text, nullable=True)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    registrations = relationship("Registration", back_populates="training")
    attendance_records = relationship("Attendance", back_populates="training")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Training(id={self.id}, title='{self.title}', status='{self.status}')>"