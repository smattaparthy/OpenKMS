import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.crud.user import user as user_crud
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


class TestUserCRUD:
    """Test cases for User CRUD operations."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def test_user_data(self):
        """Return test user data."""
        return {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "hashed_password": "hashedpassword",
            "office_location": "Test Office",
            "department": "Test Department",
            "role": UserRole.EMPLOYEE,
            "is_active": True
        }

    @pytest.mark.asyncio
    async def test_create_user(self, mock_db, test_user_data):
        """Test creating a user."""
        # Mock the query result (no existing user)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result

        # Create UserCreate object
        user_create = UserCreate(
            username=test_user_data["username"],
            email=test_user_data["email"],
            full_name=test_user_data["full_name"],
            password="password123",
            office_location=test_user_data["office_location"],
            department=test_user_data["department"]
        )

        # Mock password hashing
        with patch('app.crud.user.get_password_hash') as mock_hash:
            mock_hash.return_value = test_user_data["hashed_password"]

            # Mock the created user
            mock_user = MagicMock()
            mock_user.id = test_user_data["id"]
            mock_user.username = test_user_data["username"]
            mock_user.email = test_user_data["email"]
            mock_user.full_name = test_user_data["full_name"]
            mock_user.hashed_password = test_user_data["hashed_password"]
            mock_user.office_location = test_user_data["office_location"]
            mock_user.department = test_user_data["department"]
            mock_user.role = test_user_data["role"]
            mock_user.is_active = test_user_data["is_active"]

            # Set up the mock to return the user when add/commit is called
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            # Mock the query execution again for the refresh
            with patch.object(mock_db, 'execute', return_value=mock_result):
                result = await user_crud.create(mock_db, obj_in=user_create)

                # Assertions
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
                mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user(self, mock_db, test_user_data):
        """Test getting a user by ID."""
        # Mock the query result
        mock_user = MagicMock()
        mock_user.id = test_user_data["id"]
        mock_user.username = test_user_data["username"]
        mock_user.email = test_user_data["email"]
        mock_user.full_name = test_user_data["full_name"]
        mock_user.hashed_password = test_user_data["hashed_password"]
        mock_user.office_location = test_user_data["office_location"]
        mock_user.department = test_user_data["department"]
        mock_user.role = test_user_data["role"]
        mock_user.is_active = test_user_data["is_active"]

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_db.execute.return_value = mock_result

        result = await user_crud.get(mock_db, user_id=test_user_data["id"])

        # Assertions
        assert result == mock_user
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, mock_db):
        """Test getting a non-existent user."""
        # Mock the query result (no user found)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result

        result = await user_crud.get(mock_db, user_id=999)

        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_username(self, mock_db, test_user_data):
        """Test getting a user by username."""
        # Mock the query result
        mock_user = MagicMock()
        mock_user.username = test_user_data["username"]

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_db.execute.return_value = mock_result

        result = await user_crud.get_by_username(mock_db, username=test_user_data["username"])

        # Assertions
        assert result == mock_user
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_email(self, mock_db, test_user_data):
        """Test getting a user by email."""
        # Mock the query result
        mock_user = MagicMock()
        mock_user.email = test_user_data["email"]

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_db.execute.return_value = mock_result

        result = await user_crud.get_by_email(mock_db, email=test_user_data["email"])

        # Assertions
        assert result == mock_user
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_multi(self, mock_db, test_user_data):
        """Test getting multiple users."""
        # Mock multiple users
        mock_users = [
            MagicMock(id=1, username="user1", role=UserRole.EMPLOYEE),
            MagicMock(id=2, username="user2", role=UserRole.MANAGER),
            MagicMock(id=3, username="user3", role=UserRole.ADMIN),
        ]

        # Mock the query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_users
        mock_db.execute.return_value = mock_result

        result = await user_crud.get_multi(mock_db, skip=0, limit=10)

        # Assertions
        assert result == mock_users
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user(self, mock_db, test_user_data):
        """Test updating a user."""
        # Mock the existing user
        mock_user = MagicMock()
        mock_user.id = test_user_data["id"]
        mock_user.username = test_user_data["username"]
        mock_user.email = "old_email@example.com"
        mock_user.full_name = test_user_data["full_name"]
        mock_user.hashed_password = test_user_data["hashed_password"]
        mock_user.office_location = test_user_data["office_location"]
        mock_user.department = test_user_data["department"]
        mock_user.role = test_user_data["role"]
        mock_user.is_active = test_user_data["is_active"]

        # Create UserUpdate object
        user_update = UserUpdate(
            email="new_email@example.com",
            full_name="Updated User"
        )

        # Mock the database operations
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        result = await user_crud.update(mock_db, db_obj=mock_user, obj_in=user_update)

        # Assertions
        assert result == mock_user
        assert mock_user.email == "new_email@example.com"
        assert mock_user.full_name == "Updated User"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_user(self, mock_db, test_user_data):
        """Test removing a user."""
        # Mock the user to be removed
        mock_user = MagicMock()
        mock_user.id = test_user_data["id"]

        # Mock the database operations
        mock_db.delete.return_value = None
        mock_db.commit.return_value = None

        result = await user_crud.remove(mock_db, user_id=test_user_data["id"])

        # Assertions
        assert result == mock_user
        mock_db.delete.assert_called_once_with(mock_user)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, mock_db, test_user_data):
        """Test successful user authentication."""
        # Mock the user query result
        mock_user = MagicMock()
        mock_user.id = test_user_data["id"]
        mock_user.username = test_user_data["username"]
        mock_user.hashed_password = test_user_data["hashed_password"]
        mock_user.is_active = True

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_db.execute.return_value = mock_result

        # Mock password verification
        with patch('app.crud.user.verify_password') as mock_verify:
            mock_verify.return_value = True

            result = await user_crud.authenticate(
                mock_db, username=test_user_data["username"], password="correct_password"
            )

            # Assertions
            assert result == mock_user
            mock_verify.assert_called_once_with("correct_password", test_user_data["hashed_password"])

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, mock_db, test_user_data):
        """Test authentication with wrong password."""
        # Mock the user query result
        mock_user = MagicMock()
        mock_user.id = test_user_data["id"]
        mock_user.username = test_user_data["username"]
        mock_user.hashed_password = test_user_data["hashed_password"]
        mock_user.is_active = True

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_db.execute.return_value = mock_result

        # Mock password verification (returns False)
        with patch('app.crud.user.verify_password') as mock_verify:
            mock_verify.return_value = False

            result = await user_crud.authenticate(
                mock_db, username=test_user_data["username"], password="wrong_password"
            )

            # Assertions
            assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, mock_db):
        """Test authentication with non-existent user."""
        # Mock the query result (no user found)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result

        result = await user_crud.authenticate(mock_db, username="nonexistent", password="password")

        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_inactive(self, mock_db, test_user_data):
        """Test authentication with inactive user."""
        # Mock the user query result
        mock_user = MagicMock()
        mock_user.id = test_user_data["id"]
        mock_user.username = test_user_data["username"]
        mock_user.hashed_password = test_user_data["hashed_password"]
        mock_user.is_active = False

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_db.execute.return_value = mock_result

        # Mock password verification
        with patch('app.crud.user.verify_password') as mock_verify:
            mock_verify.return_value = True

            result = await user_crud.authenticate(
                mock_db, username=test_user_data["username"], password="correct_password"
            )

            # Assertions
            assert result is None

    @pytest.mark.asyncio
    async def test_search_users(self, mock_db):
        """Test searching users with filters."""
        # Mock search results
        mock_users = [
            MagicMock(id=1, username="john_doe", email="john@example.com", role=UserRole.EMPLOYEE),
            MagicMock(id=2, username="jane_doe", email="jane@example.com", role=UserRole.MANAGER),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_users
        mock_db.execute.return_value = mock_result

        result = await user_crud.search(
            mock_db,
            query="doe",
            role=UserRole.EMPLOYEE,
            skip=0,
            limit=10
        )

        # Assertions
        assert result == mock_users
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_active_user(self, mock_db, test_user_data):
        """Test checking if user is active."""
        # Mock the user query result
        mock_user = MagicMock()
        mock_user.id = test_user_data["id"]
        mock_user.username = test_user_data["username"]
        mock_user.is_active = True

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_db.execute.return_value = mock_result

        result = await user_crud.is_active(mock_db, user_id=test_user_data["id"])

        # Assertions
        assert result is True

    @pytest.mark.asyncio
    async def test_is_admin_user(self, mock_db, test_user_data):
        """Test checking if user is admin."""
        # Mock the user query result
        mock_user = MagicMock()
        mock_user.id = test_user_data["id"]
        mock_user.username = test_user_data["username"]
        mock_user.role = UserRole.ADMIN

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_db.execute.return_value = mock_result

        result = await user_crud.is_admin(mock_db, user_id=test_user_data["id"])

        # Assertions
        assert result is True