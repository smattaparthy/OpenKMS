import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from datetime import timedelta

from app.services.auth import AuthService
from app.schemas.user import UserLogin, UserCreate
from app.core.security import get_password_hash
from app.models.user import User, UserRole


class TestAuthService:
    """Test cases for AuthService."""

    @pytest.fixture
    def auth_service(self):
        """Create an AuthService instance."""
        service = AuthService()
        service.settings = MagicMock()
        service.settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        return service

    @pytest.mark.asyncio
    async def test_login_user_success(self, auth_service):
        """Test successful user login."""
        # Mock dependencies
        mock_db = AsyncMock()
        mock_user_crud = MagicMock()

        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.full_name = "Test User"
        mock_user.role = UserRole.EMPLOYEE
        mock_user.is_active = True

        # Mock user_crud.authenticate to return user
        with patch('app.services.auth.user_crud', mock_user_crud):
            mock_user_crud.authenticate.return_value = mock_user

            # Mock token creation
            with patch('app.services.auth.create_access_token') as mock_access_token, \
                 patch('app.services.auth.create_refresh_token') as mock_refresh_token:

                mock_access_token.return_value = "access_token"
                mock_refresh_token.return_value = "refresh_token"

                # Create login data
                login_data = UserLogin(username="testuser", password="password123")

                # Call method
                result = await auth_service.login_user(mock_db, login_data)

                # Assertions
                mock_user_crud.authenticate.assert_called_once_with(
                    mock_db, username="testuser", password="password123"
                )
                mock_access_token.assert_called_once()
                mock_refresh_token.assert_called_once()

                expected_result = {
                    "access_token": "access_token",
                    "refresh_token": "refresh_token",
                    "token_type": "bearer",
                    "user": {
                        "id": 1,
                        "username": "testuser",
                        "email": "test@example.com",
                        "full_name": "Test User",
                        "role": "EMPLOYEE"
                    }
                }
                assert result == expected_result

    @pytest.mark.asyncio
    async def test_login_user_invalid_credentials(self, auth_service):
        """Test login with invalid credentials."""
        # Mock dependencies
        mock_db = AsyncMock()
        mock_user_crud = MagicMock()

        with patch('app.services.auth.user_crud', mock_user_crud):
            mock_user_crud.authenticate.return_value = None

            login_data = UserLogin(username="testuser", password="wrongpassword")

            # Should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.login_user(mock_db, login_data)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_login_user_inactive_account(self, auth_service):
        """Test login with inactive account."""
        # Mock dependencies
        mock_db = AsyncMock()
        mock_user_crud = MagicMock()

        # Mock inactive user
        mock_user = MagicMock()
        mock_user.is_active = False

        with patch('app.services.auth.user_crud', mock_user_crud):
            mock_user_crud.authenticate.return_value = mock_user

            login_data = UserLogin(username="testuser", password="password123")

            # Should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.login_user(mock_db, login_data)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Account is disabled"

    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service):
        """Test successful user registration."""
        # Mock dependencies
        mock_db = AsyncMock()
        mock_user_crud = MagicMock()

        # Mock created user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "newuser"
        mock_user.email = "newuser@example.com"
        mock_user.full_name = "New User"
        mock_user.role = UserRole.EMPLOYEE

        with patch('app.services.auth.user_crud', mock_user_crud):
            # Mock that user doesn't exist
            mock_user_crud.get_by_username.return_value = None
            mock_user_crud.get_by_email.return_value = None
            mock_user_crud.create.return_value = mock_user

            # Mock token creation
            with patch('app.services.auth.create_access_token') as mock_access_token, \
                 patch('app.services.auth.create_refresh_token') as mock_refresh_token:

                mock_access_token.return_value = "access_token"
                mock_refresh_token.return_value = "refresh_token"

                # Create registration data
                register_data = UserCreate(
                    username="newuser",
                    email="newuser@example.com",
                    full_name="New User",
                    password="password123"
                )

                # Call method
                result = await auth_service.register_user(mock_db, register_data)

                # Assertions
                mock_user_crud.get_by_username.assert_called_once_with(
                    mock_db, username="newuser"
                )
                mock_user_crud.get_by_email.assert_called_once_with(
                    mock_db, email="newuser@example.com"
                )
                mock_user_crud.create.assert_called_once()

                expected_result = {
                    "access_token": "access_token",
                    "refresh_token": "refresh_token",
                    "token_type": "bearer",
                    "user": {
                        "id": 1,
                        "username": "newuser",
                        "email": "newuser@example.com",
                        "full_name": "New User",
                        "role": "EMPLOYEE"
                    },
                    "message": "User registered successfully"
                }
                assert result == expected_result

    @pytest.mark.asyncio
    async def test_register_user_username_exists(self, auth_service):
        """Test registration with existing username."""
        # Mock dependencies
        mock_db = AsyncMock()
        mock_user_crud = MagicMock()

        with patch('app.services.auth.user_crud', mock_user_crud):
            # Mock that username already exists
            mock_user_crud.get_by_username.return_value = MagicMock()
            mock_user_crud.get_by_email.return_value = None

            register_data = UserCreate(
                username="existinguser",
                email="newuser@example.com",
                full_name="New User",
                password="password123"
            )

            # Should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.register_user(mock_db, register_data)

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert exc_info.value.detail == "Username already registered"

    @pytest.mark.asyncio
    async def test_register_user_email_exists(self, auth_service):
        """Test registration with existing email."""
        # Mock dependencies
        mock_db = AsyncMock()
        mock_user_crud = MagicMock()

        with patch('app.services.auth.user_crud', mock_user_crud):
            # Mock that email already exists
            mock_user_crud.get_by_username.return_value = None
            mock_user_crud.get_by_email.return_value = MagicMock()

            register_data = UserCreate(
                username="newuser",
                email="existing@email.com",
                full_name="New User",
                password="password123"
            )

            # Should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.register_user(mock_db, register_data)

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert exc_info.value.detail == "Email already registered"

    @pytest.mark.asyncio
    async def test_refresh_tokens_success(self, auth_service):
        """Test successful token refresh."""
        # Mock dependencies
        mock_db = AsyncMock()
        mock_user_crud = MagicMock()

        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.is_active = True

        with patch('app.services.auth.user_crud', mock_user_crud), \
             patch('app.services.auth.create_access_token') as mock_access_token, \
             patch('app.services.auth.create_refresh_token') as mock_refresh_token, \
             patch('app.services.auth.verify_refresh_token') as mock_verify:

            # Mock refresh token verification
            mock_verify.return_value = {"sub": "testuser"}
            mock_user_crud.get_by_username.return_value = mock_user
            mock_access_token.return_value = "new_access_token"
            mock_refresh_token.return_value = "new_refresh_token"

            # Call method
            result = await auth_service.refresh_tokens(mock_db, "valid_refresh_token")

            # Assertions
            mock_verify.assert_called_once_with("valid_refresh_token")
            mock_user_crud.get_by_username.assert_called_once_with(mock_db, username="testuser")
            mock_access_token.assert_called_once()
            mock_refresh_token.assert_called_once()

            expected_result = {
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "token_type": "bearer"
            }
            assert result == expected_result

    @pytest.mark.asyncio
    async def test_refresh_tokens_invalid_token(self, auth_service):
        """Test refresh with invalid token."""
        # Mock dependencies
        mock_db = AsyncMock()

        with patch('app.services.auth.verify_refresh_token') as mock_verify:
            mock_verify.return_value = None

            # Should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.refresh_tokens(mock_db, "invalid_token")

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Invalid refresh token"

    @pytest.mark.asyncio
    async def test_refresh_tokens_user_not_found(self, auth_service):
        """Test refresh with non-existent user."""
        # Mock dependencies
        mock_db = AsyncMock()
        mock_user_crud = MagicMock()

        with patch('app.services.auth.user_crud', mock_user_crud), \
             patch('app.services.auth.verify_refresh_token') as mock_verify:

            mock_verify.return_value = {"sub": "nonexistent"}
            mock_user_crud.get_by_username.return_value = None

            # Should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.refresh_tokens(mock_db, "valid_refresh_token")

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "User not found or inactive"

    @pytest.mark.asyncio
    async def test_change_password_success(self, auth_service):
        """Test successful password change."""
        # Mock dependencies
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.hashed_password = get_password_hash("old_password")

        with patch('app.services.auth.get_password_hash') as mock_hash, \
             patch('app.services.auth.verify_password') as mock_verify:

            mock_verify.return_value = True
            mock_hash.return_value = "new_hashed_password"

            result = await auth_service.change_password(
                mock_db, 1, "old_password", "new_password"
            )

            # Assertions
            mock_verify.assert_called_once_with("old_password", mock_user.hashed_password)
            mock_hash.assert_called_once_with("new_password")
            assert mock_user.hashed_password == "new_hashed_password"
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_user)

            expected_result = {"message": "Password changed successfully"}
            assert result == expected_result

    @pytest.mark.asyncio
    async def test_change_password_wrong_current_password(self, auth_service):
        """Test password change with wrong current password."""
        # Mock dependencies
        mock_db = AsyncMock()
        mock_user_crud = MagicMock()
        mock_user = MagicMock()
        mock_user.hashed_password = get_password_hash("correct_password")

        with patch('app.services.auth.user_crud', mock_user_crud), \
             patch('app.services.auth.verify_password') as mock_verify:

            mock_user_crud.get.return_value = mock_user
            mock_verify.return_value = False

            # Should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.change_password(
                    mock_db, 1, "wrong_password", "new_password"
                )

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert exc_info.value.detail == "Current password is incorrect"