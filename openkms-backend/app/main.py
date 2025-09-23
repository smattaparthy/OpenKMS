from fastapi import FastAPI, HTTPException
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging

from app.core.config import get_settings
from app.core.database import engine, Base
# Import router after all dependencies are available

# Configure logging
logging.basicConfig(level=get_settings().LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title=get_settings().PROJECT_NAME,
    description="OpenKMS - Enterprise Knowledge Management System",
    version="1.0.0",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers (import here to avoid circular dependencies)
from app.api.v1.router import api_router
app.include_router(api_router, prefix=get_settings().API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {get_settings().PROJECT_NAME}",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )