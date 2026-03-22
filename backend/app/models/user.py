from sqlalchemy import Column, String, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base import Base, UUIDMixin, TimestampMixin
from app.core.enums import UserRole


class User(Base, UUIDMixin, TimestampMixin):
    """User account for platform authentication and profile management."""

    __tablename__ = "users"

    email         = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name    = Column(String(100), nullable=False)
    last_name     = Column(String(100), nullable=False)
    role          = Column(SAEnum(UserRole), nullable=False, default=UserRole.buyer)
    is_active          = Column(Boolean, default=True,  nullable=False)
    is_email_verified  = Column(Boolean, default=False, nullable=False)
    avatar_object_name = Column(String(500), nullable=True)
