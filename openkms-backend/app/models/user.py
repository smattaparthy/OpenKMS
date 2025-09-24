from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum as PyEnum
import uuid


class UserRole(PyEnum):
    EMPLOYEE = "employee"
    KNOWLEDGE_MANAGER = "knowledge_manager"
    ADMIN = "admin"


class User(Base):
    """User model for OpenKMS."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, name="user_role"), default=UserRole.EMPLOYEE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    office_location = Column(String(50), nullable=True)
    department = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    registrations = relationship("Registration", back_populates="user")
    attendance_records = relationship("Attendance", foreign_keys="Attendance.user_id", back_populates="user")
    recorded_attendance = relationship("Attendance", foreign_keys="Attendance.recorded_by", back_populates="recorder")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"