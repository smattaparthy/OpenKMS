from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.registration import Registration, RegistrationStatus
from app.schemas.registration import RegistrationCreate, RegistrationUpdate


class CRUDRegistration(CRUDBase[Registration, RegistrationCreate, RegistrationUpdate]):
    """CRUD operations for Registration model."""

    async def get_user_registrations(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Registration]:
        """Get all registrations for a user."""
        result = await db.execute(
            select(Registration)
            .options(
                selectinload(Registration.training),
                selectinload(Registration.user)
            )
            .where(Registration.user_id == user_id)
            .order_by(Registration.registration_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_training_registrations(
        self,
        db: AsyncSession,
        training_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Registration]:
        """Get all registrations for a training."""
        result = await db.execute(
            select(Registration)
            .options(
                selectinload(Registration.user),
                selectinload(Registration.training)
            )
            .where(Registration.training_id == training_id)
            .order_by(Registration.registration_date)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_user_registration_for_training(
        self,
        db: AsyncSession,
        user_id: int,
        training_id: int
    ) -> Optional[Registration]:
        """Get user's registration for a specific training."""
        result = await db.execute(
            select(Registration)
            .where(
                and_(
                    Registration.user_id == user_id,
                    Registration.training_id == training_id,
                    Registration.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: RegistrationCreate,
        user_id: int
    ) -> Registration:
        """Create a new registration for a user."""
        # Check if user is already registered
        existing = await self.get_user_registration_for_training(
            db, user_id=user_id, training_id=obj_in.training_id
        )
        if existing:
            raise ValueError("User is already registered for this training")

        db_obj = Registration(
            user_id=user_id,
            training_id=obj_in.training_id,
            notes=obj_in.notes,
            special_requirements=obj_in.special_requirements,
            status=RegistrationStatus.PENDING
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def confirm_registration(
        self,
        db: AsyncSession,
        registration_id: int
    ) -> Registration:
        """Confirm a registration."""
        registration = await self.get(db, registration_id)
        if registration:
            registration.status = RegistrationStatus.CONFIRMED
            registration.confirmed_date = func.now()
            await db.commit()
            await db.refresh(registration)
        return registration

    async def cancel_registration(
        self,
        db: AsyncSession,
        registration_id: int,
        reason: Optional[str] = None
    ) -> Registration:
        """Cancel a registration."""
        registration = await self.get(db, registration_id)
        if registration:
            registration.status = RegistrationStatus.CANCELLED
            registration.cancelled_date = func.now()
            registration.cancellation_reason = reason
            await db.commit()
            await db.refresh(registration)
        return registration

    async def get_confirmed_registrations_for_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Registration]:
        """Get confirmed registrations for a user."""
        result = await db.execute(
            select(Registration)
            .options(selectinload(Registration.training))
            .where(
                and_(
                    Registration.user_id == user_id,
                    Registration.status == RegistrationStatus.CONFIRMED,
                    Registration.is_active == True
                )
            )
            .order_by(Registration.registration_date)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_active_registrations(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Registration]:
        """Get all active registrations."""
        result = await db.execute(
            select(Registration)
            .options(
                selectinload(Registration.user),
                selectinload(Registration.training)
            )
            .where(Registration.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def count_registrations_by_training(
        self,
        db: AsyncSession,
        training_id: int,
        status: Optional[RegistrationStatus] = None
    ) -> int:
        """Count registrations for a training, optionally by status."""
        stmt = select(func.count(Registration.id)).where(
            Registration.training_id == training_id
        )

        if status:
            stmt = stmt.where(Registration.status == status)

        result = await db.execute(stmt)
        return result.scalar()

    async def check_capacity(
        self,
        db: AsyncSession,
        training_id: int
    ) -> dict:
        """Check training capacity and registration status."""
        # Get training with max participants
        from app.crud.training import training
        training = await training.get(db, training_id)
        if not training:
            raise ValueError("Training not found")

        confirmed_count = await self.count_registrations_by_training(
            db, training_id, RegistrationStatus.CONFIRMED
        )
        active_count = await self.count_registrations_by_training(
            db, training_id
        )

        return {
            "max_participants": training.max_participants,
            "current_participants": training.current_participants,
            "confirmed_registrations": confirmed_count,
            "active_registrations": active_count,
            "available_spots": training.max_participants - confirmed_count,
            "is_full": confirmed_count >= training.max_participants
        }


registration = CRUDRegistration(Registration)