from uuid import UUID

from app.exceptions import LocationNotFoundError, LocationSlugAlreadyExistsError
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.core.enums import UserRole
from app.schemas.location import (
    LocationCreate,
    LocationUpdate,
    LocationOut,
    LocationDetail,
    LocationListResponse,
    TagOut,
)
from app.services.location_service import location_service

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/tags", response_model=list[TagOut])
async def get_tags(db: AsyncSession = Depends(get_db)):
    """All tags for FilterPanel and TourBuilder."""
    return await location_service.get_all_tags(db)


@router.get("", response_model=LocationListResponse)
async def list_locations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tags: list[str] = Query(default=[]),
    region: str | None = Query(default=None),
    price_max: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    items, total = await location_service.get_list(
        db,
        page=page,
        page_size=page_size,
        tag_slugs=tags or None,
        region=region,
        price_max=price_max,
        only_active=True,
    )
    return LocationListResponse(
        items=items, total=total, page=page, page_size=page_size
    )


@router.get("/{slug}", response_model=LocationDetail)
async def get_location(slug: str, db: AsyncSession = Depends(get_db)):
    try:
        location_by_slug = await location_service.get_by_slug(db, slug)
    except LocationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return location_by_slug


@router.post("", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
async def create_location(
    data: LocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (UserRole.seller, UserRole.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can create locations",
        )
    try:
        created_location = await location_service.create(db, data, seller_id=current_user.id)
    except LocationSlugAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location with this slug already exists"
        )
    return created_location


@router.put("/{location_id}", response_model=LocationOut)
async def update_location(
    location_id: UUID,
    data: LocationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        location = await location_service.get_by_id(db, location_id)
    except LocationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )
    if current_user.role != UserRole.admin and location.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your location"
        )
    try:
        return await location_service.update(db, location, data)
    except LocationSlugAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Location with this slug already exists")


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        location = await location_service.get_by_id(db, location_id)
    except LocationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )
    if current_user.role != UserRole.admin and location.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your location"
        )
    await location_service.delete(db, location)


@router.patch("/{location_id}/activate", response_model=LocationOut)
async def activate_location(
    location_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admins only"
        )
    try:
        location = await location_service.get_by_id(db, location_id)
    except LocationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )
    return await location_service.set_active(db, location, is_active=True)
