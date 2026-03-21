from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import PostNotFoundError
from app.models.post import Post
from app.schemas.post import PostCreate


class PostService:

    async def get_feed(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        tags: list[str] | None = None,
        location_id: UUID | None = None,
    ):
        q = select(Post).where(Post.is_moderated == True)

        if location_id:
            q = q.where(Post.location_id == location_id)
        if tags:
            for tag in tags:
                q = q.where(Post.tags.contains([tag]))

        count_q = select(func.count()).select_from(q.subquery())
        total = (await db.execute(count_q)).scalar_one()

        q = q.order_by(Post.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(q)
        items = result.scalars().all()

        return items, total

    async def get_by_id(self, db: AsyncSession, post_id: UUID) -> Post:
        result = await db.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()
        if not post:
            raise PostNotFoundError(post_id=post_id)
        return post

    async def create(
        self,
        db: AsyncSession,
        data: PostCreate,
        author_id: UUID,
    ) -> Post:
        post = Post(
            title=data.title,
            content=data.content,
            photos=data.photos,
            tags=data.tags,
            location_id=data.location_id,
            lat=data.lat,
            lng=data.lng,
            address=data.address,
            author_id=author_id,
        )
        db.add(post)
        await db.flush()
        await db.refresh(post)
        return post

    async def like(self, db: AsyncSession, post: Post) -> Post:
        post.likes_count += 1
        await db.flush()
        await db.refresh(post)
        return post

    async def delete(self, db: AsyncSession, post: Post) -> None:
        await db.delete(post)


post_service = PostService()