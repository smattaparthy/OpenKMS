from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum as PyEnum
import uuid


class RegistrationStatus(PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    WAITLISTED = "waitlisted"
    CANCELLED = "cancelled"


class Registration(Base):
    """Registration model for training sessions."""

    __tablename__ = "registrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    training_id = Column(UUID(as_uuid=True), ForeignKey("trainings.id"), nullable=False)
    status = Column(Enum(RegistrationStatus), default=RegistrationStatus.PENDING, nullable=False)

    # Registration details
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_date = Column(DateTime(timezone=True), nullable=True)
    cancelled_date = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(String(500), nullable=True)

    # Notes
    notes = Column(String(1000), nullable=True)
    special_requirements = Column(String(500), nullable=True)

    # Administrative fields
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="registrations")
    training = relationship("Training", back_populates="registrations")
    attendance_records = relationship("Attendance", back_populates="registration")

    def __repr__(self):
        return f"<Registration(id={self.id}, user_id={self.user_id}, training_id={self.training_id}, status='{self.status}')>"