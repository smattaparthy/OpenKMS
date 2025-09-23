from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model."""

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username."""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_with_registrations(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Optional[User]:
        """Get user with registration data loaded."""
        result = await db.execute(
            select(User)
            .options(selectinload(User.registrations))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def authenticate(
        self,
        db: AsyncSession,
        username: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user with username and password."""
        user = await self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: UserCreate
    ) -> User:
        """Create a new user with hashed password."""
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            full_name=obj_in.full_name,
            hashed_password=get_password_hash(obj_in.password),
            office_location=obj_in.office_location,
            department=obj_in.department,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: UserUpdate
    ) -> User:
        """Update user, optionally handling password updates."""
        obj_data = obj_in.dict(exclude_unset=True)
        if "password" in obj_data:
            obj_data["hashed_password"] = get_password_hash(obj_data["password"])
            del obj_data["password"]

        for field, value in obj_data.items():
            setattr(db_obj, field, value)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def search(
        self,
        db: AsyncSession,
        *,
        query: Optional[str] = None,
        role: Optional[UserRole] = None,
        office_location: Optional[str] = None,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Search users with various filters."""
        stmt = select(User)

        conditions = []
        if query:
            conditions.append(
                or_(
                    User.username.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                    User.full_name.ilike(f"%{query}%")
                )
            )

        if role:
            conditions.append(User.role == role)

        if office_location:
            conditions.append(User.office_location == office_location)

        if department:
            conditions.append(User.department == department)

        if is_active is not None:
            conditions.append(User.is_active == is_active)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def count_search(
        self,
        db: AsyncSession,
        *,
        query: Optional[str] = None,
        role: Optional[UserRole] = None,
        office_location: Optional[str] = None,
        department: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """Count users matching search criteria."""
        from sqlalchemy import func

        stmt = select(func.count(User.id))

        conditions = []
        if query:
            conditions.append(
                or_(
                    User.username.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                    User.full_name.ilike(f"%{query}%")
                )
            )

        if role:
            conditions.append(User.role == role)

        if office_location:
            conditions.append(User.office_location == office_location)

        if department:
            conditions.append(User.department == department)

        if is_active is not None:
            conditions.append(User.is_active == is_active)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await db.execute(stmt)
        return result.scalar()


user = CRUDUser(User)