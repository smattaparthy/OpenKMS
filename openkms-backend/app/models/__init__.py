# Import all models here for Alembic to discover them
from .user import User, UserRole
from .training import Training, TrainingCategory, TrainingLevel, TrainingStatus
from .registration import Registration, RegistrationStatus
from .attendance import Attendance, AttendanceStatus

# Make all models available
__all__ = [
    # User model and enums
    "User",
    "UserRole",

    # Training model and enums
    "Training",
    "TrainingCategory",
    "TrainingLevel",
    "TrainingStatus",

    # Registration model and enums
    "Registration",
    "RegistrationStatus",

    # Attendance model and enums
    "Attendance",
    "AttendanceStatus",
]