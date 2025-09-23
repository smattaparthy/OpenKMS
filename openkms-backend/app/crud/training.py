from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.training import Training, TrainingCategory, TrainingLevel, TrainingStatus
from app.schemas.training import TrainingCreate, TrainingUpdate, TrainingFilter


class CRUDTraining(CRUDBase[Training, TrainingCreate, TrainingUpdate]):
    """CRUD operations for Training model."""

    async def get_with_registrations(
        self,
        db: AsyncSession,
        training_id: int
    ) -> Optional[Training]:
        """Get training with registration data loaded."""
        result = await db.execute(
            select(Training)
            .options(selectinload(Training.registrations))
            .where(Training.id == training_id)
        )
        return result.scalar_one_or_none()

    async def get_future_trainings(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Training]:
        """Get upcoming training sessions."""
        from datetime import datetime

        result = await db.execute(
            select(Training)
            .where(Training.start_date >= datetime.utcnow())
            .where(Training.status == TrainingStatus.PUBLISHED)
            .order_by(Training.start_date)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def search(
        self,
        db: AsyncSession,
        *,
        filters: TrainingFilter,
        skip: int = 0,
        limit: int = 100
    ) -> List[Training]:
        """Search trainings with various filters."""
        stmt = select(Training).options(selectinload(Training.registrations))

        conditions = []

        if filters.search:
            search_term = f"%{filters.search}%"
            conditions.append(
                or_(
                    Training.title.ilike(search_term),
                    Training.description.ilike(search_term),
                    Training.instructor.ilike(search_term)
                )
            )

        if filters.category:
            conditions.append(Training.category == filters.category)

        if filters.level:
            conditions.append(Training.level == filters.level)

        if filters.location:
            conditions.append(Training.location == filters.location)

        if filters.status:
            conditions.append(Training.status == filters.status)

        if filters.start_date_from:
            conditions.append(Training.start_date >= filters.start_date_from)

        if filters.start_date_to:
            conditions.append(Training.start_date <= filters.start_date_to)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(Training.start_date).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def count_search(
        self,
        db: AsyncSession,
        *,
        filters: TrainingFilter
    ) -> int:
        """Count trainings matching search criteria."""
        stmt = select(func.count(Training.id))

        conditions = []

        if filters.search:
            search_term = f"%{filters.search}%"
            conditions.append(
                or_(
                    Training.title.ilike(search_term),
                    Training.description.ilike(search_term),
                    Training.instructor.ilike(search_term)
                )
            )

        if filters.category:
            conditions.append(Training.category == filters.category)

        if filters.level:
            conditions.append(Training.level == filters.level)

        if filters.location:
            conditions.append(Training.location == filters.location)

        if filters.status:
            conditions.append(Training.status == filters.status)

        if filters.start_date_from:
            conditions.append(Training.start_date >= filters.start_date_from)

        if filters.start_date_to:
            conditions.append(Training.start_date <= filters.start_date_to)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await db.execute(stmt)
        return result.scalar()

    async def update_participant_count(
        self,
        db: AsyncSession,
        training_id: int,
        increment: int = 1
    ) -> Training:
        """Update participant count for a training."""
        training = await self.get(db, training_id=training_id)
        if training:
            training.current_participants += increment
            await db.commit()
            await db.refresh(training)
        return training

    async def get_available_trainings(
        self,
        db: AsyncSession,
        *,
        location: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Training]:
        """Get trainings with available spots."""
        stmt = (
            select(Training)
            .where(
                and_(
                    Training.status == TrainingStatus.PUBLISHED,
                    Training.current_participants < Training.max_participants,
                    Training.start_date >= func.now()
                )
            )
            .order_by(Training.start_date)
            .offset(skip)
            .limit(limit)
        )

        if location:
            stmt = stmt.where(Training.location == location)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_trainings_by_instructor(
        self,
        db: AsyncSession,
        instructor_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Training]:
        """Get trainings created by a specific instructor."""
        result = await db.execute(
            select(Training)
            .where(Training.created_by == instructor_id)
            .order_by(Training.start_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


training = CRUDTraining(Training)