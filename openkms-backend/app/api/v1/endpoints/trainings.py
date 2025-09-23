from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_db, get_current_user, get_current_admin_user, get_optional_user
from app.crud.training import training as training_crud
from app.schemas.training import (
    Training, TrainingCreate, TrainingUpdate, TrainingFilter, TrainingList
)
from app.models.user import User as UserModel
from app.models.training import TrainingStatus

router = APIRouter()


@router.get("/", response_model=TrainingList)
async def get_trainings(
    search: Optional[str] = Query(None, description="Search in title, description, or instructor"),
    category: Optional[str] = Query(None, description="Filter by category"),
    level: Optional[str] = Query(None, description="Filter by level"),
    location: Optional[str] = Query(None, description="Filter by location"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date_from: Optional[str] = Query(None, description="Start date from (ISO format)"),
    start_date_to: Optional[str] = Query(None, description="Start date to (ISO format)"),
    page: int = Query(1, gt=0, description="Page number"),
    size: int = Query(20, gt=0, le=100, description="Page size"),
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[UserModel] = Depends(get_optional_user)
):
    """
    Get list of trainings with advanced filtering and search.

    - **search**: Search across title, description, and instructor
    - **category**: Filter by training category
    - **level**: Filter by difficulty level
    - **location**: Filter by physical location
    - **status**: Filter by training status
    - **start_date_from/t_to**: Date range filtering
    - **page**: Page number for pagination
    - **size**: Number of items per page (max 100)
    """
    from datetime import datetime

    # Create filter object
    filters = TrainingFilter(
        search=search,
        category=category,
        level=level,
        location=location,
        status=status,
        start_date_from=datetime.fromisoformat(start_date_from) if start_date_from else None,
        start_date_to=datetime.fromisoformat(start_date_to) if start_date_to else None
    )

    # Calculate pagination
    skip = (page - 1) * size

    # Get trainings
    trainings = await training_crud.search(db, filters=filters, skip=skip, limit=size)

    # Get total count
    total = await training_crud.count_search(db, filters=filters)

    # Format response with additional data
    formatted_trainings = []
    for training in trainings:
        available_spots = training.max_participants - training.current_participants

        training_data = {
            "id": training.id,
            "title": training.title,
            "description": training.description,
            "category": training.category.value,
            "level": training.level.value,
            "status": training.status.value,
            "location": training.location,
            "max_participants": training.max_participants,
            "current_participants": training.current_participants,
            "available_spots": available_spots,
            "start_date": training.start_date,
            "end_date": training.end_date,
            "duration_hours": training.duration_hours,
            "credits_required": training.credits_required,
            "cost": training.cost,
            "instructor": training.instructor,
            "created_at": training.created_at,
            "creator_name": training.creator.full_name if training.creator else None
        }

        formatted_trainings.append(training_data)

    return {
        "trainings": formatted_trainings,
        "total": total,
        "page": page,
        "size": size
    }


@router.get("/upcoming", response_model=List[dict])
async def get_upcoming_trainings(
    location: Optional[str] = Query(None, description="Filter by location"),
    limit: int = Query(10, gt=0, le=50, description="Maximum number to return"),
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[UserModel] = Depends(get_optional_user)
):
    """
    Get upcoming published trainings.

    - **location**: Filter by office location
    - **limit**: Maximum number of trainings to return
    """
    trainings = await training_crud.get_future_trainings(db, skip=0, limit=limit)

    if location:
        trainings = [t for t in trainings if t.location == location]

    return [
        {
            "id": training.id,
            "title": training.title,
            "category": training.category.value,
            "location": training.location,
            "start_date": training.start_date,
            "duration_hours": training.duration_hours,
            "instructor": training.instructor,
            "available_spots": training.max_participants - training.current_participants
        }
        for training in trainings
    ]


@router.get("/available", response_model=List[dict])
async def get_available_trainings(
    location: Optional[str] = Query(None, description="Filter by location"),
    limit: int = Query(20, gt=0, le=100, description="Maximum number to return"),
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[UserModel] = Depends(get_optional_user)
):
    """
    Get trainings with available spots.

    - **location**: Filter by office location
    - **limit**: Maximum number of trainings to return
    """
    trainings = await training_crud.get_available_trainings(db, location=location, skip=0, limit=limit)

    return [
        {
            "id": training.id,
            "title": training.title,
            "category": training.category.value,
            "level": training.level.value,
            "location": training.location,
            "start_date": training.start_date,
            "duration_hours": training.duration_hours,
            "credits_required": training.credits_required,
            "available_spots": training.max_participants - training.current_participants,
            "instructor": training.instructor
        }
        for training in trainings
    ]


@router.get("/{training_id}", response_model=dict)
async def get_training(
    training_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[UserModel] = Depends(get_optional_user)
):
    """
    Get training details by ID.

    - **training_id**: Training ID to retrieve
    """
    training = await training_crud.get_with_registrations(db, training_id=training_id)
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found"
        )

    return {
        "id": training.id,
        "title": training.title,
        "description": training.description,
        "category": training.category.value,
        "level": training.level.value,
        "status": training.status.value,
        "location": training.location,
        "max_participants": training.max_participants,
        "current_participants": training.current_participants,
        "available_spots": training.max_participants - training.current_participants,
        "start_date": training.start_date,
        "end_date": training.end_date,
        "duration_hours": training.duration_hours,
        "credits_required": training.credits_required,
        "cost": training.cost,
        "instructor": training.instructor,
        "prerequisites": training.prerequisites,
        "learning_objectives": training.learning_objectives,
        "created_by": training.created_by,
        "created_at": training.created_at,
        "updated_at": training.updated_at,
        "creator_name": training.creator.full_name if training.creator else None,
        "registration_count": len(training.registrations)
    }


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_training(
    training_data: TrainingCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Create a new training (Admin only).

    - **training_data**: Training creation data
    """
    # Add created_by from current user
    training = await training_crud.create(
        db,
        obj_in=training_data
    )

    # Set created_by field
    training.created_by = current_user.id
    await db.commit()
    await db.refresh(training)

    return {
        "id": training.id,
        "message": "Training created successfully"
    }


@router.put("/{training_id}", response_model=dict)
async def update_training(
    training_id: int,
    training_data: TrainingUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Update training information (Admin only).

    - **training_id**: Training ID to update
    - **training_data**: Training update data
    """
    training = await training_crud.get(db, training_id=training_id)
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found"
        )

    updated_training = await training_crud.update(db, db_obj=training, obj_in=training_data)

    return {
        "id": updated_training.id,
        "message": "Training updated successfully"
    }


@router.delete("/{training_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training(
    training_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Delete training (Admin only).

    - **training_id**: Training ID to delete
    """
    training = await training_crud.get(db, training_id=training_id)
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found"
        )

    # Check if there are active registrations
    from app.crud.registration import registration as registration_crud
    has_registrations = await registration_crud.count_registrations_by_training(db, training_id)

    if has_registrations > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete training with existing registrations"
        )

    await training_crud.remove(db, id=training_id)


@router.post("/{training_id}/publish", response_model=dict)
async def publish_training(
    training_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Publish a training (Admin only).

    - **training_id**: Training ID to publish
    """
    training = await training_crud.get(db, training_id=training_id)
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found"
        )

    if training.status == TrainingStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Training is already published"
        )

    # Update status
    training.status = TrainingStatus.PUBLISHED
    await db.commit()
    await db.refresh(training)

    return {
        "id": training.id,
        "status": training.status.value,
        "message": "Training published successfully"
    }