from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.core.enums import UserRole
from app.exceptions import PostNotFoundError
from app.schemas.post import PostCreate, PostOut, PostListResponse
from app.services.post_service import post_service

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=PostListResponse)
async def get_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tags: list[str] = Query(default=[]),
    location_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    items, total = await post_service.get_feed(
        db,
        page=page,
        page_size=page_size,
        tags=tags or None,
        location_id=location_id,
    )
    return PostListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{post_id}", response_model=PostOut)
async def get_post(post_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        return await post_service.get_by_id(db, post_id)
    except PostNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await post_service.create(db, data, author_id=current_user.id)


@router.post("/{post_id}/like", response_model=PostOut)
async def like_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        post = await post_service.get_by_id(db, post_id)
    except PostNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return await post_service.like(db, post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        post = await post_service.get_by_id(db, post_id)
    except PostNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your post")
    await post_service.delete(db, post)