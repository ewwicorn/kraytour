import uuid

from sqlalchemy import Column, String, Boolean, Float, Integer, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base

location_tag_association = Table(
    "location_tags",
    Base.metadata,
    Column("location_id", UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    """Location category tag for filtering and organization."""

    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    label_ru = Column(String(200), nullable=False)
    group = Column(String(100), nullable=False)
    subgroup = Column(String(100), nullable=True)


class Location(Base):
    """Tourism location/attraction with pricing and availability details."""

    __tablename__ = "locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String(150), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    address = Column(String(500), nullable=True)
    region = Column(String(100), nullable=True, default="Краснодарский край")
    photos = Column(ARRAY(Text), nullable=False, default=list)
    price_from = Column(Integer, nullable=True)
    price_to = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    avg_temp_summer = Column(Float, nullable=True)
    avg_temp_winter = Column(Float, nullable=True)
    duration_hours_min = Column(Float, nullable=True)
    duration_hours_max = Column(Float, nullable=True)
    group_size_min = Column(Integer, nullable=True)
    group_size_max = Column(Integer, nullable=True)

    seller = relationship("User", foreign_keys=[seller_id], lazy="selectin")
    tags = relationship("Tag", secondary=location_tag_association, lazy="selectin")
