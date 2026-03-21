from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime


class AuthorShort(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    title: str
    content: Optional[str] = None
    photos: list[str] = []
    tags: Optional[list[str]] = None
    location_id: Optional[UUID] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = None
    
    @field_validator("location_id", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class PostOut(BaseModel):
    id: UUID
    title: str
    content: Optional[str] = None
    photos: list[str]
    tags: Optional[list[str]] = None
    location_id: Optional[UUID] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = None
    author_id: Optional[UUID] = None
    likes_count: int
    is_moderated: bool
    created_at: datetime
    author: Optional[AuthorShort] = None

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    items: list[PostOut]
    total: int
    page: int
    page_size: int