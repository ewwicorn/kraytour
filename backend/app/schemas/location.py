from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class TagOut(BaseModel):
    """Location tag response schema."""

    id: UUID
    slug: str
    label_ru: str
    group: str
    subgroup: Optional[str] = None

    class Config:
        from_attributes = True

class LocationCreate(BaseModel):
    """Location creation request schema."""

    slug: str
    name: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    lat: float
    lng: float
    address: Optional[str] = None
    region: str = "Краснодарский край"
    photos: list[str] = []
    price_from: Optional[int] = None
    price_to: Optional[int] = None
    tag_ids: list[UUID] = []
    avg_temp_summer: Optional[float] = None
    avg_temp_winter: Optional[float] = None
    duration_hours_min: Optional[float] = None
    duration_hours_max: Optional[float] = None
    group_size_min: Optional[int] = None
    group_size_max: Optional[int] = None


class LocationUpdate(BaseModel):
    """Location update request schema."""

    name: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = None
    photos: Optional[list[str]] = None
    price_from: Optional[int] = None
    price_to: Optional[int] = None
    tag_ids: Optional[list[UUID]] = None
    avg_temp_summer: Optional[float] = None
    avg_temp_winter: Optional[float] = None
    duration_hours_min: Optional[float] = None
    duration_hours_max: Optional[float] = None
    group_size_min: Optional[int] = None
    group_size_max: Optional[int] = None


class SellerShort(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class LocationOut(BaseModel):
    id: UUID
    slug: str
    name: str
    short_description: Optional[str] = None
    lat: float
    lng: float
    address: Optional[str] = None
    region: str
    photos: list[str]
    price_from: Optional[int] = None
    price_to: Optional[int] = None
    is_active: bool
    is_featured: bool
    tags: list[TagOut] = []
    seller: Optional[SellerShort] = None

    class Config:
        from_attributes = True


class LocationDetail(LocationOut):
    description: Optional[str] = None
    avg_temp_summer: Optional[float] = None
    avg_temp_winter: Optional[float] = None
    duration_hours_min: Optional[float] = None
    duration_hours_max: Optional[float] = None
    group_size_min: Optional[int] = None
    group_size_max: Optional[int] = None


class LocationListResponse(BaseModel):
    items: list[LocationOut]
    total: int
    page: int
    page_size: int
