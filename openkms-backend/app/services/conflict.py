from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.crud.registration import registration as registration_crud
from app.crud.training import training as training_crud
from app.models.registration import RegistrationStatus
from app.models.training import TrainingStatus


class ConflictDetectionService:
    """Service for detecting schedule conflicts and other registration issues."""

    async def detect_schedule_conflicts(
        self,
        db: AsyncSession,
        user_id: int,
        training_id: int
    ) -> List[Dict[str, Any]]:
        """
        Detect schedule conflicts for user registration.

        Args:
            db: Database session
            user_id: User ID registering for training
            training_id: Training ID being registered for

        Returns:
            List of conflict objects with details
        """
        conflicts = []

        # Get target training details
        target_training = await training_crud.get(db, training_id=training_id)
        if not target_training:
            conflicts.append({
                "type": "training_not_found",
                "message": "Target training not found",
                "severity": "error"
            })
            return conflicts

        # Get user's confirmed registrations with overlapping timeframes
        user_registrations = await registration_crud.get_confirmed_registrations_for_user(
            db, user_id=user_id
        )

        for registration in user_registrations:
            if not registration.training:
                continue

            # Skip if it's the same training (already registered)
            if registration.training.id == training_id:
                conflicts.append({
                    "type": "duplicate_registration",
                    "message": "Already registered for this training",
                    "severity": "error",
                    "training": {
                        "id": registration.training.id,
                        "title": registration.training.title,
                        "start_date": registration.training.start_date.isoformat()
                    }
                })
                continue

            # Check for time overlap
            if await self._check_time_overlap(
                target_training.start_date,
                target_training.end_date,
                registration.training.start_date,
                registration.training.end_date
            ):
                conflicts.append({
                    "type": "schedule_overlap",
                    "message": "Time conflict with existing training",
                    "severity": "error",
                    "conflicting_training": {
                        "id": registration.training.id,
                        "title": registration.training.title,
                        "start_date": registration.training.start_date.isoformat(),
                        "end_date": registration.training.end_date.isoformat(),
                        "location": registration.training.location
                    }
                })

        # Check for location conflicts (same time, different location might still be an issue)
        await self._check_location_conflicts(db, user_id, target_training, conflicts)

        # Check for same-day multiple trainings warning
        await self._check_same_day_conflicts(db, user_id, target_training, conflicts)

        return conflicts

    async def _check_time_overlap(
        self,
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        """Check if two time ranges overlap."""
        # Consider a small buffer between trainings (30 minutes)
        buffer_minutes = 30
        buffer = timedelta(minutes=buffer_minutes)

        # Adjust times with buffer
        adjusted_start1 = start1 - buffer
        adjusted_end1 = end1 + buffer

        return (
            adjusted_start1 < end2 and adjusted_end1 > start2
        )

    async def _check_location_conflicts(
        self,
        db: AsyncSession,
        user_id: int,
        target_training: Any,
        conflicts: List[Dict[str, Any]]
    ):
        """Check for conflicts requiring travel time between different locations."""
        user_registrations = await registration_crud.get_confirmed_registrations_for_user(
            db, user_id=user_id
        )

        # Define minimum travel time between different offices (in hours)
        office_travel_times = {
            ("NYC", "Boston"): 4.0,
            ("NYC", "Dallas"): 6.0,
            ("Boston", "Dallas"): 8.0,
            # Reverse directions
            ("Boston", "NYC"): 4.0,
            ("Dallas", "NYC"): 6.0,
            ("Dallas", "Boston"): 8.0,
            # Same location
            ("NYC", "NYC"): 0.0,
            ("Boston", "Boston"): 0.0,
            ("Dallas", "Dallas"): 0.0
        }

        for registration in user_registrations:
            if not registration.training:
                continue

            location1 = target_training.location
            location2 = registration.training.location

            travel_time = office_travel_times.get(
                (location1, location2),
                office_travel_times.get((location2, location1), 0.0)
            )

            # If locations are different and require significant travel time
            if travel_time > 0:
                if await self._check_insufficient_travel_time(
                    target_training.start_date,
                    target_training.end_date,
                    registration.training.start_date,
                    registration.training.end_date,
                    travel_time
                ):
                    conflicts.append({
                        "type": "travel_time_conflict",
                        "message": f"Insufficient travel time between {location1} and {location2}",
                        "severity": "warning",
                        "travel_time_hours": travel_time,
                        "conflicting_training": {
                            "id": registration.training.id,
                            "title": registration.training.title,
                            "start_date": registration.training.start_date.isoformat(),
                            "end_date": registration.training.end_date.isoformat(),
                            "location": registration.training.location
                        }
                    })

    async def _check_insufficient_travel_time(
        self,
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime,
        travel_time_hours: float
    ) -> bool:
        """Check if there's sufficient travel time between trainings."""
        travel_time_delta = timedelta(hours=travel_time_hours)
        minimum_gap = travel_time_delta + timedelta(hours=1)  # Travel time + 1 hour buffer

        # Check if trainings are on the same day
        if start1.date() != start2.date():
            return False

        # Check if gap between trainings is less than required travel time
        if end1 < start2:
            gap = start2 - end1
            return gap < minimum_gap

        if end2 < start1:
            gap = start1 - end2
            return gap < minimum_gap

        return False

    async def _check_same_day_conflicts(
        self,
        db: AsyncSession,
        user_id: int,
        target_training: Any,
        conflicts: List[Dict[str, Any]]
    ):
        """Check for multiple trainings on the same day (warning level)."""
        target_date = target_training.start_date.date()

        # Get all confirmed registrations on the same day
        user_registrations = await registration_crud.get_confirmed_registrations_for_user(
            db, user_id=user_id
        )

        same_day_trainings = [
            reg for reg in user_registrations
            if (reg.training and
                reg.training.start_date.date() == target_date and
                reg.training.id != target_training.id)
        ]

        if len(same_day_trainings) >= 2:
            conflicts.append({
                "type": "same_day_multiple_trainings",
                "message": f"Already have {len(same_day_trainings)} training(s) on this day",
                "severity": "warning",
                "training_date": target_date.isoformat(),
                "existing_trainings": [
                    {
                        "id": reg.training.id,
                        "title": reg.training.title,
                        "start_time": reg.training.start_date.strftime("%H:%M"),
                        "end_time": reg.training.end_date.strftime("%H:%M")
                    }
                    for reg in same_day_trainings
                ]
            })

    async def validate_registration_prerequisites(
        self,
        db: AsyncSession,
        user_id: int,
        training_id: int
    ) -> List[Dict[str, Any]]:
        """Validate if user meets registration prerequisites."""
        validation_issues = []

        # Get training details
        training = await training_crud.get(db, training_id=training_id)
        if not training:
            validation_issues.append({
                "type": "training_not_found",
                "message": "Training not found",
                "severity": "error"
            })
            return validation_issues

        # Check if user has completed required prerequisites
        if training.prerequisites:
            # This would need more sophisticated logic to check completed trainings
            # For now, we'll add a placeholder
            pass

        # Check if user has sufficient credits (if applicable)
        # This would require user profile/credits management
        pass

        # Check if training is full
        capacity_info = await registration_crud.check_capacity(db, training_id)
        if capacity_info["is_full"]:
            validation_issues.append({
                "type": "training_full",
                "message": "Training is at full capacity",
                "severity": "error"
            })

        return validation_issues