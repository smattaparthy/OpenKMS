# Import all schemas here for easy access
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    User,
    UserInDB,
    UserLogin,
    Token,
    TokenPayload
)

from .training import (
    TrainingFilter,
    TrainingBase,
    TrainingCreate,
    TrainingUpdate,
    Training,
    TrainingList
)

from .registration import (
    RegistrationCreate,
    RegistrationUpdate,
    Registration,
    RegistrationList,
    ConflictResponse,
    RegistrationResponse
)

# Make all schemas available
__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "User",
    "UserInDB",
    "UserLogin",
    "Token",
    "TokenPayload",

    # Training schemas
    "TrainingFilter",
    "TrainingBase",
    "TrainingCreate",
    "TrainingUpdate",
    "Training",
    "TrainingList",

    # Registration schemas
    "RegistrationCreate",
    "RegistrationUpdate",
    "Registration",
    "RegistrationList",
    "ConflictResponse",
    "RegistrationResponse",
]