import pytest
from fastapi.testclient import TestClient
from fastapi import status
import pytest_asyncio


class TestAuthAPI:
    """Integration tests for authentication API endpoints."""

    def test_register_user_success(self, client, test_user_data):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert "message" in data

        user_data = data["user"]
        assert user_data["username"] == test_user_data["username"]
        assert user_data["email"] == test_user_data["email"]
        assert user_data["full_name"] == test_user_data["full_name"]
        assert user_data["role"] == "EMPLOYEE"

    def test_register_user_duplicate_username(self, client, test_user, test_user_data):
        """Test registration with duplicate username."""
        # User already exists from fixture
        response = client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Username already registered" in data["detail"]

    def test_register_user_duplicate_email(self, client, test_user, test_user_data_2):
        """Test registration with duplicate email."""
        # Create a new user with same email as existing user
        duplicate_email_data = test_user_data_2.copy()
        duplicate_email_data["email"] = test_user.email

        response = client.post("/api/v1/auth/register", json=duplicate_email_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Email already registered" in data["detail"]

    def test_register_user_validation_error(self, client):
        """Test registration with invalid data."""
        invalid_data = {
            "username": "",  # Empty username
            "email": "invalid-email",  # Invalid email
            "full_name": "T",  # Too short name
            "password": "123"  # Too short password
        }

        response = client.post("/api/v1/auth/register", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_user_success(self, client, test_user):
        """Test successful user login."""
        login_data = {
            "username": test_user.username,
            "password": "testpassword123"
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

        user_data = data["user"]
        assert user_data["username"] == test_user.username
        assert user_data["email"] == test_user.email
        assert user_data["full_name"] == test_user.full_name
        assert user_data["role"] == test_user.role.value

    def test_login_user_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        login_data = {
            "username": test_user.username,
            "password": "wrongpassword"
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Invalid credentials" in data["detail"]

    def test_login_user_nonexistent_user(self, client):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent",
            "password": "anypassword"
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Invalid credentials" in data["detail"]

    def test_refresh_token_success(self, client, test_user):
        """Test successful token refresh."""
        # First login to get refresh token
        login_data = {
            "username": test_user.username,
            "password": "testpassword123"
        }

        login_response = client.post("/api/v1/auth/login", json=login_data)
        login_data_response = login_response.json()
        refresh_token = login_data_response["refresh_token"]

        # Now refresh the token
        refresh_data = {"refresh_token": refresh_token}

        response = client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        # Ensure new tokens are different from old ones
        assert data["access_token"] != login_data_response["access_token"]
        assert data["refresh_token"] != refresh_token

    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token."""
        refresh_data = {"refresh_token": "invalid_token"}

        response = client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Invalid refresh token" in data["detail"]

    def test_change_password_success(self, client, test_user):
        """Test successful password change."""
        auth_headers = {
            "Authorization": f"Bearer {self._get_user_token(client, test_user)}"
        }

        change_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }

        response = client.post("/api/v1/auth/change-password",
                               headers=auth_headers,
                               json=change_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Password changed successfully"

        # Test login with new password
        login_data = {
            "username": test_user.username,
            "password": "newpassword123"
        }

        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK

    def test_change_password_wrong_current(self, client, test_user):
        """Test password change with wrong current password."""
        auth_headers = {
            "Authorization": f"Bearer {self._get_user_token(client, test_user)}"
        }

        change_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }

        response = client.post("/api/v1/auth/change-password",
                               headers=auth_headers,
                               json=change_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Current password is incorrect" in data["detail"]

    def test_change_password_no_auth(self, client, test_user):
        """Test password change without authentication."""
        change_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }

        response = client.post("/api/v1/auth/change-password", json=change_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_info_success(self, client, test_user):
        """Test getting current user info successfully."""
        auth_headers = {
            "Authorization": f"Bearer {self._get_user_token(client, test_user)}"
        }

        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "user" in data
        user_data = data["user"]

        assert user_data["id"] == test_user.id
        assert user_data["username"] == test_user.username
        assert user_data["email"] == test_user.email
        assert user_data["full_name"] == test_user.full_name
        assert user_data["office_location"] == test_user.office_location
        assert user_data["department"] == test_user.department
        assert user_data["role"] == test_user.role.value
        assert user_data["is_active"] == test_user.is_active

    def test_get_current_user_info_no_auth(self, client):
        """Test getting current user info without authentication."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_info_invalid_token(self, client):
        """Test getting current user info with invalid token."""
        auth_headers = {"Authorization": "Bearer invalid_token"}

        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def _get_user_token(self, client, test_user):
        """Helper method to get user token."""
        login_data = {
            "username": test_user.username,
            "password": "testpassword123"
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        return response.json()["access_token"]


class TestAuthAPIAsync:
    """Async integration tests for authentication API endpoints."""

    @pytest.mark.asyncio
    async def test_async_register_login_flow(self, async_client, test_user_data):
        """Test async register and login flow."""
        # Register user
        register_response = await async_client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        register_data = register_response.json()
        access_token = register_data["access_token"]

        # Test protected endpoint with token
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        me_response = await async_client.get("/api/v1/auth/me", headers=auth_headers)

        assert me_response.status_code == status.HTTP_200_OK
        user_data = me_response.json()["user"]
        assert user_data["username"] == test_user_data["username"]
        assert user_data["email"] == test_user_data["email"]

    @pytest.mark.asyncio
    async def test_async_concurrent_requests(self, async_client, test_user):
        """Test handling of concurrent requests."""
        import asyncio

        # Get token for user
        login_data = {
            "username": test_user.username,
            "password": "testpassword123"
        }

        login_response = await async_client.post("/api/v1/auth/login", json=login_data)
        access_token = login_response.json()["access_token"]

        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Make concurrent requests
        async def make_request():
            return await async_client.get("/api/v1/auth/me", headers=auth_headers)

        tasks = [make_request() for _ in range(5)]
        responses = await asyncio.gather(*tasks)

        # All requests should succeed
        for response in responses:
            assert response.status_code == status.HTTP_200_OK

        # All should return the same user data
        user_data = responses[0].json()["user"]
        assert user_data["username"] == test_user.username

    @pytest.mark.asyncio
    async def test_async_token_lifecycle(self, async_client, test_user_data):
        """Test complete async token lifecycle."""
        # Register
        register_response = await async_client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        register_data = register_response.json()
        refresh_token = register_data["refresh_token"]

        # Use token
        access_token = register_data["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        me_response = await async_client.get("/api/v1/auth/me", headers=auth_headers)
        assert me_response.status_code == status.HTTP_200_OK

        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        refresh_response = await async_client.post("/api/v1/auth/refresh", json=refresh_data)
        assert refresh_response.status_code == status.HTTP_200_OK

        refresh_data_response = refresh_response.json()
        new_access_token = refresh_data_response["access_token"]

        # Use new token
        new_auth_headers = {"Authorization": f"Bearer {new_access_token}"}
        new_me_response = await async_client.get("/api/v1/auth/me", headers=new_auth_headers)
        assert new_me_response.status_code == status.HTTP_200_OK

        # Verify same user data
        original_user = me_response.json()["user"]
        new_user = new_me_response.json()["user"]
        assert original_user["username"] == new_user["username"]