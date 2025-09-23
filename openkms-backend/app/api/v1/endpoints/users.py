from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_db, get_current_user, get_current_admin_user
from app.crud.user import user as user_crud
from app.schemas.user import User, UserUpdate, UserCreate, UserRole
from app.models.user import User as UserModel

router = APIRouter()


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "office_location": current_user.office_location,
        "department": current_user.department,
        "role": current_user.role.value,
        "is_active": current_user.is_active
    }


@router.get("/", response_model=List[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search by username, email, or name"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    office_location: Optional[str] = Query(None, description="Filter by office location"),
    department: Optional[str] = Query(None, description="Filter by department"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Get list of users with optional filtering (Admin only).

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **search**: Search text to filter users
    - **role**: Filter by user role
    - **office_location**: Filter by office location
    - **department**: Filter by department
    - **is_active**: Filter by active status
    """
    users = await user_crud.search(
        db,
        query=search,
        role=role,
        office_location=office_location,
        department=department,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    return users


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get user by ID.

    - **user_id**: User ID to retrieve
    """
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user"
        )

    user = await user_crud.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update user information.

    - **user_id**: User ID to update
    - **user_update**: Updated user data
    """
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    user = await user_crud.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Non-admin users cannot change role or active status
    if current_user.role != UserRole.ADMIN:
        if user_update.role is not None or user_update.is_active is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to change role or active status"
            )

    updated_user = await user_crud.update(db, db_obj=user, obj_in=user_update)
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Delete user (Admin only).

    - **user_id**: User ID to delete
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    user = await user_crud.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await user_crud.remove(db, id=user_id)


@router.get("/me/registrations", response_model=List[dict])
async def get_my_registrations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get current user's training registrations.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    registrations = await user_crud.get_with_registrations(db, current_user.id)

    # Format response
    response_data = []
    for registration in registrations.registrations if registrations else []:
        response_data.append({
            "id": registration.id,
            "training": {
                "id": registration.training.id,
                "title": registration.training.title,
                "category": registration.training.category.value,
                "start_date": registration.training.start_date,
                "location": registration.training.location,
                "status": registration.training.status.value
            },
            "registration": {
                "status": registration.status.value,
                "registration_date": registration.registration_date,
                "confirmed_date": registration.confirmed_date,
                "notes": registration.notes
            }
        })

    return response_data[skip:skip + limit]


@router.get("/me/attendance", response_model=List[dict])
async def get_my_attendance(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get current user's attendance records.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    # This would be implemented with attendance CRUD
    # For now, return empty list
    return []