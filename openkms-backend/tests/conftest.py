import asyncio
import pytest
from typing import Generator, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest_asyncio

from app.core.database import get_async_db
from app.core.config import get_settings
from app.main import app
from app.models.base import Base
from app.core.security import get_password_hash

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/openkms_test"

# Override settings for testing
def get_test_settings():
    from app.core.config import Settings
    return Settings(
        DATABASE_URL=TEST_DATABASE_URL,
        SECRET_KEY="test-secret-key-not-for-production",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        ALGORITHM="HS256",  # Use faster algorithm for testing
        ENVIRONMENT="testing"
    )

# Test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,  # Disable SQL logging for tests
    pool_pre_ping=True,
)

# Test session factory
TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db_setup():
    """Set up test database tables and tear them down after tests."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def test_session(test_db_setup) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.fixture
def test_db(test_session):
    """Override the database dependency for testing."""
    async def override_get_db():
        yield test_session
    return override_get_db

@pytest.fixture
def client(test_db):
    """Create a test client for the FastAPI app."""
    app.dependency_overrides[get_async_db] = test_db
    app.dependency_overrides[get_settings] = get_test_settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def async_client(test_db) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    app.dependency_overrides[get_async_db] = test_db
    app.dependency_overrides[get_settings] = get_test_settings
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data():
    """Return test user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123",
        "office_location": "Test Office",
        "department": "Test Department"
    }

@pytest.fixture
def test_user_data_2():
    """Return second test user data."""
    return {
        "username": "testuser2",
        "email": "test2@example.com",
        "full_name": "Test User 2",
        "password": "testpassword123",
        "office_location": "Test Office 2",
        "department": "Test Department 2"
    }

@pytest.fixture
def test_admin_data():
    """Return test admin user data."""
    return {
        "username": "testadmin",
        "email": "admin@example.com",
        "full_name": "Test Admin",
        "password": "adminpassword123",
        "office_location": "Admin Office",
        "department": "Administration"
    }

@pytest.fixture
def test_training_data():
    """Return test training data."""
    return {
        "title": "Test Training Session",
        "description": "A test training session for testing purposes",
        "category": "TECHNICAL",
        "level": "INTERMEDIATE",
        "start_date": "2024-01-15T09:00:00",
        "end_date": "2024-01-15T17:00:00",
        "location": "Test Conference Room",
        "max_participants": 25,
        "instructor": "Test Instructor",
        "status": "SCHEDULED"
    }

@pytest_asyncio.fixture
async def test_user(test_session, test_user_data):
    """Create a test user in the database."""
    from app.models.user import User, UserRole

    user = User(
        username=test_user_data["username"],
        email=test_user_data["email"],
        full_name=test_user_data["full_name"],
        hashed_password=get_password_hash(test_user_data["password"]),
        office_location=test_user_data["office_location"],
        department=test_user_data["department"],
        role=UserRole.EMPLOYEE,
        is_active=True
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    return user

@pytest_asyncio.fixture
async def test_admin(test_session, test_admin_data):
    """Create a test admin user in the database."""
    from app.models.user import User, UserRole

    user = User(
        username=test_admin_data["username"],
        email=test_admin_data["email"],
        full_name=test_admin_data["full_name"],
        hashed_password=get_password_hash(test_admin_data["password"]),
        office_location=test_admin_data["office_location"],
        department=test_admin_data["department"],
        role=UserRole.ADMIN,
        is_active=True
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    return user

@pytest_asyncio.fixture
async def test_training(test_session, test_training_data, test_admin):
    """Create a test training session in the database."""
    from app.models.training import Training, TrainingCategory, TrainingLevel, TrainingStatus

    training = Training(
        title=test_training_data["title"],
        description=test_training_data["description"],
        category=TrainingCategory[test_training_data["category"]],
        level=TrainingLevel[test_training_data["level"]],
        start_date=test_training_data["start_date"],
        end_date=test_training_data["end_date"],
        location=test_training_data["location"],
        max_participants=test_training_data["max_participants"],
        instructor=test_training_data["instructor"],
        status=TrainingStatus[test_training_data["status"]],
        created_by=test_admin.id
    )
    test_session.add(training)
    await test_session.commit()
    await test_session.refresh(training)

    return training

@pytest.fixture
def auth_headers(client, test_user):
    """Return authentication headers for the test user."""
    response = client.post("/api/v1/auth/login", json={
        "username": test_user.username,
        "password": "testpassword123"
    })
    assert response.status_code == 200
    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}

@pytest.fixture
def admin_auth_headers(client, test_admin):
    """Return authentication headers for the test admin."""
    response = client.post("/api/v1/auth/login", json={
        "username": test_admin.username,
        "password": "adminpassword123"
    })
    assert response.status_code == 200
    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}