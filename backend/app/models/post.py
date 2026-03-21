import uuid

from sqlalchemy import Column, String, Boolean, Integer, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class Post(Base, TimestampMixin):
    """User-generated content related to locations, such as reviews or experiences."""

    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    address = Column(String(500), nullable=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    photos = Column(ARRAY(Text), nullable=False, default=list)
    tags = Column(ARRAY(Text), nullable=True)
    likes_count = Column(Integer, default=0)
    is_moderated = Column(Boolean, default=True)

    location = relationship("Location", foreign_keys=[location_id], lazy="selectin")
    author = relationship("User", foreign_keys=[author_id], lazy="selectin")