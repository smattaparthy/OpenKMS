from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, trainings, registrations

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(trainings.router, prefix="/trainings", tags=["trainings"])
api_router.include_router(registrations.router, prefix="/registrations", tags=["registrations"])