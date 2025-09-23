import pytest
from fastapi.testclient import TestClient
from fastapi import status
import pytest_asyncio


class TestUsersAPI:
    """Integration tests for users API endpoints."""

    def test_get_current_user_profile(self, client, test_user, auth_headers):
        """Test getting current user profile."""
        response = client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["office_location"] == test_user.office_location
        assert data["department"] == test_user.department
        assert data["role"] == test_user.role.value
        assert data["is_active"] == test_user.is_active

    def test_get_current_user_profile_no_auth(self, client):
        """Test getting current user profile without authentication."""
        response = client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_by_id_owner(self, client, test_user, auth_headers):
        """Test getting user by ID (owner)."""
        response = client.get(f"/api/v1/users/{test_user.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email

    def test_get_user_by_id_admin(self, client, test_user, test_admin, admin_auth_headers):
        """Test getting user by ID (admin)."""
        response = client.get(f"/api/v1/users/{test_user.id}", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email

    def test_get_user_by_id_unauthorized(self, client, test_user, test_user_data_2, auth_headers):
        """Test getting user by ID (unauthorized)."""
        # Create another user
        client.post("/api/v1/auth/register", json=test_user_data_2)
        other_user_id = test_user.id + 1  # Assume the new user has ID = current_user_id + 1

        response = client.get(f"/api/v1/users/{other_user_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not authorized to access this user" in response.json()["detail"]

    def test_get_user_not_found(self, client, test_admin, admin_auth_headers):
        """Test getting non-existent user."""
        response = client.get("/api/v1/users/999", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]

    def test_get_users_admin_success(self, client, test_user, test_admin, admin_auth_headers):
        """Test getting users list (admin)."""
        response = client.get("/api/v1/users/", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, list)
        # Should have at least the test user and admin user
        assert len(data) >= 2

        # Verify admin user is in the list
        admin_in_list = any(user["username"] == test_admin.username for user in data)
        assert admin_in_list

    def test_get_users_user_forbidden(self, client, test_user, auth_headers):
        """Test getting users list (non-admin - should be forbidden)."""
        response = client.get("/api/v1/users/", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in response.json()["detail"]

    def test_get_users_no_auth(self, client):
        """Test getting users list without authentication."""
        response = client.get("/api/v1/users/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_users_with_filters_admin(self, client, test_user, test_admin, admin_auth_headers):
        """Test getting users with filters (admin)."""
        # Test role filter
        response = client.get("/api/v1/users/?role=EMPLOYEE", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        for user in data:
            assert user["role"] == "EMPLOYEE"

        # Test search filter
        response = client.get(f"/api/v1/users/?search={test_user.username}", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should return users matching the search
        matching_users = [user for user in data if test_user.username.lower() in user["username"].lower()]
        assert len(matching_users) > 0

    def test_get_users_pagination_admin(self, client, test_user, test_admin, admin_auth_headers):
        """Test users list pagination (admin)."""
        # Test skip
        response = client.get("/api/v1/users/?skip=1", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should have fewer results
        response_all = client.get("/api/v1/users/", headers=admin_auth_headers)
        data_all = response_all.json()

        assert len(data) <= len(data_all)

        # Test limit
        response = client.get("/api/v1/users/?limit=1", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) <= 1

    def test_update_current_user_success(self, client, test_user, auth_headers):
        """Test updating current user profile."""
        update_data = {
            "full_name": "Updated Name",
            "office_location": "Updated Office",
            "department": "Updated Department"
        }

        response = client.put(f"/api/v1/users/{test_user.id}",
                             headers=auth_headers,
                             json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["full_name"] == "Updated Name"
        assert data["office_location"] == "Updated Office"
        assert data["department"] == "Updated Department"

        # Other fields should remain unchanged
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role.value

    def test_update_user_admin_success(self, client, test_user, test_admin, admin_auth_headers):
        """Test updating user as admin."""
        update_data = {
            "full_name": "Admin Updated Name",
            "role": "MANAGER"
        }

        response = client.put(f"/api/v1/users/{test_user.id}",
                             headers=admin_auth_headers,
                             json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["full_name"] == "Admin Updated Name"
        assert data["role"] == "MANAGER"

    def test_update_user_unauthorized_role_change(self, client, test_user, auth_headers):
        """Test updating user role as non-admin (should fail)."""
        update_data = {
            "role": "ADMIN"
        }

        response = client.put(f"/api/v1/users/{test_user.id}",
                             headers=auth_headers,
                             json=update_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not authorized to change role or active status" in response.json()["detail"]

    def test_update_user_unauthorized_active_change(self, client, test_user, auth_headers):
        """Test updating user active status as non-admin (should fail)."""
        update_data = {
            "is_active": False
        }

        response = client.put(f"/api/v1/users/{test_user.id}",
                             headers=auth_headers,
                             json=update_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not authorized to change role or active status" in response.json()["detail"]

    def test_update_user_not_owner_or_admin(self, client, test_user, test_user_data_2, auth_headers):
        """Test updating user without being owner or admin."""
        # Create another user
        client.post("/api/v1/auth/register", json=test_user_data_2)
        other_user_id = test_user.id + 1  # Assume the new user has ID = current_user_id + 1

        update_data = {"full_name": "Hacker Name"}

        response = client.put(f"/api/v1/users/{other_user_id}",
                             headers=auth_headers,
                             json=update_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not authorized to update this user" in response.json()["detail"]

    def test_update_user_not_found(self, client, test_admin, admin_auth_headers):
        """Test updating non-existent user."""
        update_data = {"full_name": "Ghost Name"}

        response = client.put("/api/v1/users/999",
                             headers=admin_auth_headers,
                             json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]

    def test_delete_user_admin_success(self, client, test_user, test_admin, admin_auth_headers):
        """Test deleting user as admin."""
        response = client.delete(f"/api/v1/users/{test_user.id}", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify user is deleted
        get_response = client.get(f"/api/v1/users/{test_user.id}", headers=admin_auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_user_forbidden(self, client, test_user, auth_headers):
        """Test deleting user as non-admin (should fail)."""
        response = client.delete(f"/api/v1/users/{test_user.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in response.json()["detail"]

    def test_delete_user_not_found(self, client, test_admin, admin_auth_headers):
        """Test deleting non-existent user."""
        response = client.delete("/api/v1/users/999", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]

    def test_delete_own_account_admin(self, client, test_admin, admin_auth_headers):
        """Test admin cannot delete own account."""
        response = client.delete(f"/api/v1/users/{test_admin.id}", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot delete your own account" in response.json()["detail"]

    def test_get_my_registrations_success(self, client, test_user, test_training, auth_headers):
        """Test getting current user's registrations."""
        response = client.get("/api/v1/users/me/registrations", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, list)

    def test_get_my_registrations_no_auth(self, client):
        """Test getting registrations without authentication."""
        response = client.get("/api/v1/users/me/registrations")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_my_registrations_pagination(self, client, test_user, test_training, auth_headers):
        """Test registrations pagination."""
        response = client.get("/api/v1/users/me/registrations?skip=0&limit=5", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_my_attendance_success(self, client, test_user, auth_headers):
        """Test getting current user's attendance."""
        response = client.get("/api/v1/users/me/attendance", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, list)
        # Should be empty as we haven't implemented attendance yet

    def test_get_my_attendance_no_auth(self, client):
        """Test getting attendance without authentication."""
        response = client.get("/api/v1/users/me/attendance")

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUsersAPIAsync:
    """Async integration tests for users API endpoints."""

    @pytest.mark.asyncio
    async def test_async_user_operations(self, async_client, test_user_data, test_admin_data):
        """Test async user CRUD operations."""
        # Register test user
        register_response = await async_client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        user_data = register_response.json()
        access_token = user_data["access_token"]
        user_id = user_data["user"]["id"]

        # Test get user profile
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = await async_client.get("/api/v1/users/me", headers=auth_headers)
        assert profile_response.status_code == status.HTTP_200_OK

        # Test update user
        update_data = {"full_name": "Async Updated Name"}
        update_response = await async_client.put(
            f"/api/v1/users/{user_id}",
            headers=auth_headers,
            json=update_data
        )
        assert update_response.status_code == status.HTTP_200_OK

        # Verify update
        updated_user = update_response.json()
        assert updated_user["full_name"] == "Async Updated Name"

        # Test get registrations
        registrations_response = await async_client.get(
            "/api/v1/users/me/registrations",
            headers=auth_headers
        )
        assert registrations_response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_async_admin_operations(self, async_client, test_admin_data, test_user_data_2):
        """Test async admin operations."""
        # Register admin
        admin_response = await async_client.post("/api/v1/auth/register", json=test_admin_data)
        assert admin_response.status_code == status.HTTP_201_CREATED

        admin_data = admin_response.json()
        admin_access_token = admin_data["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_access_token}"}

        # Register regular user
        user_response = await async_client.post("/api/v1/auth/register", json=test_user_data_2)
        assert user_response.status_code == status.HTTP_201_CREATED

        user_data = user_response.json()
        user_id = user_data["user"]["id"]

        # Test admin can get all users
        users_response = await async_client.get("/api/v1/users/", headers=admin_headers)
        assert users_response.status_code == status.HTTP_200_OK

        users_list = users_response.json()
        assert len(users_list) >= 2

        # Test admin can search users
        search_response = await async_client.get(
            f"/api/v1/users/?search={user_data['user']['username']}",
            headers=admin_headers
        )
        assert search_response.status_code == status.HTTP_200_OK

        # Test admin can update other user
        update_data = {"full_name": "Admin Modified Name"}
        update_response = await async_client.put(
            f"/api/v1/users/{user_id}",
            headers=admin_headers,
            json=update_data
        )
        assert update_response.status_code == status.HTTP_200_OK

        updated_user = update_response.json()
        assert updated_user["full_name"] == "Admin Modified Name"