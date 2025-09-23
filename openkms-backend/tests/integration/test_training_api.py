import pytest
from fastapi.testclient import TestClient
from fastapi import status
import pytest_asyncio


class TestTrainingAPI:
    """Integration tests for training API endpoints."""

    def test_create_training_admin_success(self, client, test_admin, admin_auth_headers, test_training_data):
        """Test creating training session as admin."""
        response = client.post("/api/v1/trainings/",
                             headers=admin_auth_headers,
                             json=test_training_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["title"] == test_training_data["title"]
        assert data["description"] == test_training_data["description"]
        assert data["category"] == test_training_data["category"]
        assert data["level"] == test_training_data["level"]
        assert data["location"] == test_training_data["location"]
        assert data["max_participants"] == test_training_data["max_participants"]
        assert data["instructor"] == test_training_data["instructor"]
        assert data["status"] == test_training_data["status"]
        assert "id" in data
        assert "created_at" in data

    def test_create_training_user_forbidden(self, client, test_user, auth_headers, test_training_data):
        """Test creating training session as regular user (should be forbidden)."""
        response = client.post("/api/v1/trainings/",
                             headers=auth_headers,
                             json=test_training_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in response.json()["detail"]

    def test_create_training_no_auth(self, client, test_training_data):
        """Test creating training session without authentication."""
        response = client.post("/api/v1/trainings/", json=test_training_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_training_validation_error(self, client, test_admin, admin_auth_headers):
        """Test creating training with invalid data."""
        invalid_data = {
            "title": "",  # Empty title
            "description": "Test description",
            "category": "INVALID_CATEGORY",  # Invalid category
            "level": "INVALID_LEVEL",  # Invalid level
            "start_date": "invalid-date",  # Invalid date
            "max_participants": -1,  # Negative participants
            "instructor": ""
        }

        response = client.post("/api/v1/trainings/",
                             headers=admin_auth_headers,
                             json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_trainings_public_success(self, client, test_training):
        """Test getting training sessions (public access)."""
        response = client.get("/api/v1/trainings/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= 1

        # Check first training
        first_training = data[0]
        assert "id" in first_training
        assert "title" in first_training
        assert "description" in first_training
        assert "category" in first_training
        assert "level" in first_training
        assert "status" in first_training

    def test_get_trainings_with_filters(self, client, test_training):
        """Test getting training sessions with filters."""
        # Test category filter
        response = client.get(f"/api/v1/trainings/?category={test_training.category}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        for training in data:
            assert training["category"] == test_training.category

        # Test status filter
        response = client.get(f"/api/v1/trainings/?status={test_training.status}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        for training in data:
            assert training["status"] == test_training.status

    def test_get_trainings_search(self, client, test_training):
        """Test searching training sessions."""
        search_term = "Test"
        response = client.get(f"/api/v1/trainings/?search={search_term}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should return trainings containing the search term
        matching_trainings = [t for t in data if search_term.lower() in t["title"].lower()]
        assert len(matching_trainings) > 0

    def test_get_trainings_pagination(self, client, test_training):
        """Test training sessions pagination."""
        # Test skip
        response = client.get("/api/v1/trainings/?skip=1")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        response_all = client.get("/api/v1/trainings/")
        data_all = response_all.json()

        assert len(data) <= len(data_all)

        # Test limit
        response = client.get("/api/v1/trainings/?limit=1")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) <= 1

    def test_get_training_by_id_success(self, client, test_training):
        """Test getting training session by ID."""
        response = client.get(f"/api/v1/trainings/{test_training.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == test_training.id
        assert data["title"] == test_training.title
        assert data["description"] == test_training.description
        assert data["category"] == test_training.category.value
        assert data["level"] == test_training.level.value
        assert data["status"] == test_training.status.value

    def test_get_training_not_found(self, client):
        """Test getting non-existent training session."""
        response = client.get("/api/v1/trainings/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Training not found" in response.json()["detail"]

    def test_update_training_admin_success(self, client, test_training, test_admin, admin_auth_headers):
        """Test updating training session as admin."""
        update_data = {
            "title": "Updated Training Title",
            "description": "Updated description",
            "status": "CANCELLED"
        }

        response = client.put(f"/api/v1/trainings/{test_training.id}",
                             headers=admin_auth_headers,
                             json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["title"] == "Updated Training Title"
        assert data["description"] == "Updated description"
        assert data["status"] == "CANCELLED"

        # Other fields should remain unchanged
        assert data["category"] == test_training.category.value
        assert data["level"] == test_training.level.value

    def test_update_training_user_forbidden(self, client, test_training, test_user, auth_headers):
        """Test updating training session as regular user (should be forbidden)."""
        update_data = {"title": "Hacked Title"}

        response = client.put(f"/api/v1/trainings/{test_training.id}",
                             headers=auth_headers,
                             json=update_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in response.json()["detail"]

    def test_update_training_not_found(self, client, test_admin, admin_auth_headers):
        """Test updating non-existent training session."""
        update_data = {"title": "Ghost Title"}

        response = client.put("/api/v1/trainings/999",
                             headers=admin_auth_headers,
                             json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Training not found" in response.json()["detail"]

    def test_delete_training_admin_success(self, client, test_training, test_admin, admin_auth_headers):
        """Test deleting training session as admin."""
        response = client.delete(f"/api/v1/trainings/{test_training.id}", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify training is deleted
        get_response = client.get(f"/api/v1/trainings/{test_training.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_training_user_forbidden(self, client, test_training, test_user, auth_headers):
        """Test deleting training session as regular user (should be forbidden)."""
        response = client.delete(f"/api/v1/trainings/{test_training.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in response.json()["detail"]

    def test_delete_training_not_found(self, client, test_admin, admin_auth_headers):
        """Test deleting non-existent training session."""
        response = client.delete("/api/v1/trainings/999", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Training not found" in response.json()["detail"]

    def test_get_training_registrations_admin_success(self, client, test_training, test_admin, admin_auth_headers):
        """Test getting training registrations as admin."""
        response = client.get(f"/api/v1/trainings/{test_training.id}/registrations",
                              headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, list)

    def test_get_training_registrations_user_forbidden(self, client, test_training, test_user, auth_headers):
        """Test getting training registrations as regular user (should be forbidden)."""
        response = client.get(f"/api/v1/trainings/{test_training.id}/registrations",
                              headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in response.json()["detail"]

    def test_get_training_registrations_no_auth(self, client, test_training):
        """Test getting training registrations without authentication."""
        response = client.get(f"/api/v1/trainings/{test_training.id}/registrations")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_register_for_training_success(self, client, test_training, test_user, auth_headers):
        """Test registering for training session."""
        registration_data = {
            "notes": "Looking forward to this training!"
        }

        response = client.post(f"/api/v1/trainings/{test_training.id}/register",
                              headers=auth_headers,
                              json=registration_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["training_id"] == test_training.id
        assert data["user_id"] == test_user.id
        assert data["status"] == "PENDING"
        assert data["notes"] == registration_data["notes"]
        assert "registration_date" in data

    def test_register_for_training_not_found(self, client, test_user, auth_headers):
        """Test registering for non-existent training session."""
        registration_data = {"notes": "Test notes"}

        response = client.post("/api/v1/trainings/999/register",
                              headers=auth_headers,
                              json=registration_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Training not found" in response.json()["detail"]

    def test_register_for_training_no_auth(self, client, test_training):
        """Test registering for training session without authentication."""
        registration_data = {"notes": "Test notes"}

        response = client.post(f"/api/v1/trainings/{test_training.id}/register",
                              json=registration_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_register_for_training_already_registered(self, client, test_training, test_user, auth_headers):
        """Test registering for training session already registered."""
        # First registration
        registration_data = {"notes": "First registration"}
        client.post(f"/api/v1/trainings/{test_training.id}/register",
                   headers=auth_headers,
                   json=registration_data)

        # Second registration
        response = client.post(f"/api/v1/trainings/{test_training.id}/register",
                              headers=auth_headers,
                              json=registration_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    def test_check_registration_conflicts_success(self, client, test_training, test_user, auth_headers):
        """Test checking registration conflicts."""
        response = client.post(f"/api/v1/trainings/{test_training.id}/check-conflicts",
                              headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "has_conflicts" in data
        assert "conflicts" in data
        assert isinstance(data["conflicts"], list)

    def test_check_registration_conflicts_no_auth(self, client, test_training):
        """Test checking registration conflicts without authentication."""
        response = client.post(f"/api/v1/trainings/{test_training.id}/check-conflicts")

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestTrainingAPIAsync:
    """Async integration tests for training API endpoints."""

    @pytest.mark.asyncio
    async def test_async_training_lifecycle(self, async_client, test_admin_data, test_user_data):
        """Test complete async training lifecycle."""
        # Register admin
        admin_response = await async_client.post("/api/v1/auth/register", json=test_admin_data)
        assert admin_response.status_code == status.HTTP_201_CREATED

        admin_data_response = admin_response.json()
        admin_access_token = admin_data_response["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_access_token}"}

        # Create training
        training_data = {
            "title": "Async Training Session",
            "description": "A test training for async testing",
            "category": "TECHNICAL",
            "level": "BEGINNER",
            "start_date": "2024-02-01T09:00:00",
            "end_date": "2024-02-01T17:00:00",
            "location": "Virtual Room",
            "max_participants": 30,
            "instructor": "Test Instructor",
            "status": "SCHEDULED"
        }

        create_response = await async_client.post("/api/v1/trainings/",
                                                headers=admin_headers,
                                                json=training_data)
        assert create_response.status_code == status.HTTP_201_CREATED

        created_training = create_response.json()
        training_id = created_training["id"]

        # Get training list
        list_response = await async_client.get("/api/v1/trainings/")
        assert list_response.status_code == status.HTTP_200_OK

        trainings_list = list_response.json()
        created_in_list = any(t["id"] == training_id for t in trainings_list)
        assert created_in_list

        # Get training details
        detail_response = await async_client.get(f"/api/v1/trainings/{training_id}")
        assert detail_response.status_code == status.HTTP_200_OK

        training_details = detail_response.json()
        assert training_details["title"] == training_data["title"]

        # Update training
        update_data = {"title": "Updated Async Training"}
        update_response = await async_client.put(
            f"/api/v1/trainings/{training_id}",
            headers=admin_headers,
            json=update_data
        )
        assert update_response.status_code == status.HTTP_200_OK

        # Delete training
        delete_response = await async_client.delete(
            f"/api/v1/trainings/{training_id}",
            headers=admin_headers
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = await async_client.get(f"/api/v1/trainings/{training_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_async_training_registration_flow(self, async_client, test_admin_data, test_user_data):
        """Test async training registration flow."""
        # Register admin
        admin_response = await async_client.post("/api/v1/auth/register", json=test_admin_data)
        assert admin_response.status_code == status.HTTP_201_CREATED

        admin_data_response = admin_response.json()
        admin_access_token = admin_data_response["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_access_token}"}

        # Register user
        user_response = await async_client.post("/api/v1/auth/register", json=test_user_data)
        assert user_response.status_code == status.HTTP_201_CREATED

        user_data_response = user_response.json()
        user_access_token = user_data_response["access_token"]
        user_headers = {"Authorization": f"Bearer {user_access_token}"}

        # Create training
        training_data = {
            "title": "Registration Test Training",
            "description": "Training for registration testing",
            "category": "TECHNICAL",
            "level": "BEGINNER",
            "start_date": "2024-02-01T09:00:00",
            "end_date": "2024-02-01T17:00:00",
            "location": "Virtual Room",
            "max_participants": 30,
            "instructor": "Test Instructor",
            "status": "SCHEDULED"
        }

        create_response = await async_client.post("/api/v1/trainings/",
                                                headers=admin_headers,
                                                json=training_data)
        assert create_response.status_code == status.HTTP_201_CREATED

        created_training = create_response.json()
        training_id = created_training["id"]

        # Check conflicts
        conflicts_response = await async_client.post(
            f"/api/v1/trainings/{training_id}/check-conflicts",
            headers=user_headers
        )
        assert conflicts_response.status_code == status.HTTP_200_OK

        conflicts_data = conflicts_response.json()
        assert "has_conflicts" in conflicts_data
        assert "conflicts" in conflicts_data

        # Register for training
        registration_data = {"notes": "Excited to join!"}
        register_response = await async_client.post(
            f"/api/v1/trainings/{training_id}/register",
            headers=user_headers,
            json=registration_data
        )
        assert register_response.status_code == status.HTTP_201_CREATED

        registration = register_response.json()
        assert registration["status"] == "PENDING"

        # Get user registrations (this endpoint was in the users API tests)
        user_registrations_response = await async_client.get(
            "/api/v1/users/me/registrations",
            headers=user_headers
        )
        assert user_registrations_response.status_code == status.HTTP_200_OK

        registrations = user_registrations_response.json()
        assert len(registrations) >= 1
        registered_training = next(
            (r for r in registrations if r["training"]["id"] == training_id),
            None
        )
        assert registered_training is not None