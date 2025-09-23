from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base CRUD operations with async support."""

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods for async database operations.

        Args:
            model: A SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Get a single record by ID."""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        result = await db.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType
    ) -> ModelType:
        """Create a new record."""
        obj_data = obj_in.dict()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update an existing record."""
        obj_data = obj_in.dict(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db: AsyncSession,
        *,
        id: int
    ) -> ModelType:
        """Remove a record by ID."""
        obj = await self.get(db, id=id)
        await db.delete(obj)
        await db.commit()
        return obj

    async def count(self, db: AsyncSession) -> int:
        """Count total records."""
        result = await db.execute(select(func.count(self.model.id)))
        return result.scalar()