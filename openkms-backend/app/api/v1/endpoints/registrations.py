from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_db, get_current_user, get_current_admin_user
from app.crud.registration import registration as registration_crud
from app.crud.training import training as training_crud
from app.schemas import registration as schemas
from app.models.user import User as UserModel
from app.models.registration import Registration
from app.services.conflict import ConflictDetectionService

router = APIRouter()
conflict_service = ConflictDetectionService()


@router.get("/", response_model=schemas.RegistrationList)
async def get_registrations(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    training_id: Optional[int] = Query(None, description="Filter by training ID"),
    status: Optional[str] = Query(None, description="Filter by registration status"),
    page: int = Query(1, gt=0, description="Page number"),
    size: int = Query(20, gt=0, le=100, description="Page size"),
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Get list ofregistrations with filtering (Admin only).

    - **user_id**: Filter by user ID
    - **training_id**: Filter by training ID
    - **status**: Filter by registration status
    - **page**: Page number for pagination
    - **size**: Number of items per page
    """
    skip = (page - 1) * size

    if user_id:
        registrations = await registration_crud.get_user_registrations(
            db, user_id=user_id, skip=skip, limit=size
        )
        total = len(registrations)
    elif training_id:
        registrations = await registration_crud.get_training_registrations(
            db, training_id=training_id, skip=skip, limit=size
        )
        total = len(registrations)
    else:
        registrations = await registration_crud.get_active_registrations(
            db, skip=skip, limit=size
        )
        total = await registration_crud.count(db)  # This would need to be implemented

    # Format response
    formatted_registrations = []
    for reg in registrations:
        formatted_registrations.append({
            "id": reg.id,
            "user_id": reg.user_id,
            "user_name": reg.user.full_name if reg.user else None,
            "office_location": reg.user.office_location if reg.user else None,
            "training_id": reg.training_id,
            "training_title": reg.training.title if reg.training else None,
            "trainer_name": reg.training.instructor if reg.training else None,
            "status": reg.status.value,
            "registration_date": reg.registration_date,
            "confirmed_date": reg.confirmed_date,
            "cancelled_date": reg.cancelled_date,
            "notes": reg.notes,
            "special_requirements": reg.special_requirements,
            "is_active": reg.is_active,
            "created_at": reg.created_at,
            "updated_at": reg.updated_at
        })

    return {
        "registrations": formatted_registrations,
        "total": total,
        "page": page,
        "size": size
    }


@router.get("/my-registrations", response_model=schemas.RegistrationList)
async def get_my_registrations(
    page: int = Query(1, gt=0, description="Page number"),
    size: int = Query(20, gt=0, le=100, description="Page size"),
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get current user's training registrations.

    - **page**: Page number for pagination
    - **size**: Number of items per page
    """
    skip = (page - 1) * size
    registrations = await registration_crud.get_user_registrations(
        db, user_id=current_user.id, skip=skip, limit=size
    )

    # Get total count
    from sqlalchemy import func, select
    result = await db.execute(
        select(func.count(Registration.id))
        .where(Registration.user_id == current_user.id)
        .where(Registration.is_active == True)
    )
    total = result.scalar()

    # Format response
    formatted_registrations = []
    for reg in registrations:
        formatted_registrations.append({
            "id": reg.id,
            "user_id": reg.user_id,
            "training_id": reg.training_id,
            "training_title": reg.training.title if reg.training else None,
            "trainer_name": reg.training.instructor if reg.training else None,
            "status": reg.status.value,
            "registration_date": reg.registration_date,
            "confirmed_date": reg.confirmed_date,
            "cancelled_date": reg.cancelled_date,
            "notes": reg.notes,
            "created_at": reg.created_at,
            "updated_at": reg.updated_at
        })

    return {
        "registrations": formatted_registrations,
        "total": total,
        "page": page,
        "size": size
    }


@router.get("/{registration_id}", response_model=schemas.Registration)
async def get_registration(
    registration_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get registration details by ID.

    - **registration_id**: Registration ID to retrieve
    """
    registration = await registration_crud.get(db, registration_id=registration_id)
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    # CheckPermissions: users can only see their own registrations, admins can see all
    if (current_user.id != registration.user_id and
        current_user.role.value != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this registration"
        )

    return registration


@router.post("/{training_id}/check-conflicts", response_model=schemas.ConflictResponse)
async def check_registration_conflicts(
    training_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Check for scheduling conflicts before registration.

    - **training_id**: Training ID to check conflicts for
    """
    # Get training details
    training = await training_crud.get(db, training_id=training_id)
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found"
        )

    # Check for conflicts
    conflicts = await conflict_service.detect_schedule_conflicts(
        db, current_user.id, training_id
    )

    return {
        "has_conflicts": len(conflicts) > 0,
        "conflicts": conflicts
    }


@router.post("/{training_id}/register", response_model=schemas.RegistrationResponse)
async def register_for_training(
    training_id: int,
    notes: Optional[str] = None,
    special_requirements: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Register for a training session.

    - **training_id**: Training ID to register for
    - **notes**: Optional registration notes
    - **special_requirements**: Optional special requirements
    """
    # Check if training exists and is published
    training = await training_crud.get(db, training_id=training_id)
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found"
        )

    # Check if training is published
    if training.status.value != "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Training is not open for registration"
        )

    # Check capacity
    capacity_info = await registration_crud.check_capacity(db, training_id)
    if capacity_info["is_full"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Training is full"
        )

    # Check for conflicts
    conflicts = await conflict_service.detect_schedule_conflicts(
        db, current_user.id, training_id
    )

    if conflicts:
        return RegistrationResponse(
            status="conflict_detected",
            registration_id=0,
            message="Schedule conflicts detected",
            conflicts=conflicts
        )

    # Create registration
    try:
        registration_data = schemas.RegistrationCreate(
            training_id=training_id,
            notes=notes,
            special_requirements=special_requirements
        )

        registration = await registration_crud.create(
            db, obj_in=registration_data, user_id=current_user.id
        )

        # Update training participant count
        await training_crud.update_participant_count(db, training_id, 1)

        return RegistrationResponse(
            status="registered",
            registration_id=registration.id,
            message="Successfully registered for training"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{registration_id}/confirm", response_model=dict)
async def confirm_registration(
    registration_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Confirm a registration (Admin only).

    - **registration_id**: Registration ID to confirm
    """
    registration = await registration_crud.confirm_registration(db, registration_id)
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    return {
        "id": registration.id,
        "status": registration.status.value,
        "message": "Registration confirmed successfully"
    }


@router.post("/{registration_id}/cancel", response_model=dict)
async def cancel_registration(
    registration_id: int,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Cancel a registration.

    - **registration_id**: Registration ID to cancel
    - **reason**: Optional reason for cancellation
    """
    registration = await registration_crud.get(db, registration_id=registration_id)
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    # CheckPermissions: users can only cancel their own registrations, admins can cancel all
    if (current_user.id != registration.user_id and
        current_user.role.value != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this registration"
        )

    # Cancel registration
    cancelled_registration = await registration_crud.cancel_registration(
        db, registration_id, reason
    )

    # Update training participant count
    await training_crud.update_participant_count(db, registration.training_id, -1)

    return {
        "id": cancelled_registration.id,
        "status": cancelled_registration.status.value,
        "message": "Registration cancelled successfully"
    }