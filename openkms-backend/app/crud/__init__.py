# Import all CRUD operations here for easy access
from .base import CRUDBase
from .user import user, CRUDUser
from .training import training, CRUDTraining
from .registration import registration, CRUDRegistration

# Make all CRUD operations available
__all__ = [
    "CRUDBase",
    "user",
    "CRUDUser",
    "training",
    "CRUDTraining",
    "registration",
    "CRUDRegistration",
]