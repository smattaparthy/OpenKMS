from sqlalchemy import Column, Integer, String, Integer, DateTime, Enum, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum as PyEnum


class AttendanceStatus(PyEnum):
    PRESENT = "present"
    ABSENT = "absent"
    TARDY = "tardy"
    EARLY_DEPARTURE = "early_departure"
    EXCUSED_ABSENCE = "excused_absence"


class Attendance(Base):
    """Attendance tracking model."""

    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    training_id = Column(Integer, ForeignKey("trainings.id"), nullable=False)
    registration_id = Column(Integer, ForeignKey("registrations.id"), nullable=True)

    # Attendance details
    status = Column(Enum(AttendanceStatus), nullable=False)
    check_in_time = Column(DateTime(timezone=True), nullable=True)
    check_out_time = Column(DateTime(timezone=True), nullable=True)
    hours_attended = Column(Float, nullable=True)

    # Admin information
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(String(1000), nullable=True)

    # Credit and completion
    credits_earned = Column(Float, default=0.0, nullable=False)
    certificate_issued = Column(Boolean, default=False, nullable=False)
    certificate_date = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="attendance_records")
    training = relationship("Training", back_populates="attendance_records")
    registration = relationship("Registration", back_populates="attendance_records")
    recorder = relationship("User", foreign_keys=[recorded_by])

    def __repr__(self):
        return f"<Attendance(id={self.id}, user_id={self.user_id}, training_id={self.training_id}, status='{self.status}')>"