"""
models/user.py — пользователь системы.

Одна запись на человека независимо от роли.
Роль определяет какой профиль заполнен: buyer_profile или seller_profile.
Аватар хранится в MinIO, здесь только путь к объекту.
"""
from sqlalchemy import Column, String, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base import Base, UUIDMixin, TimestampMixin
from app.core.enums import UserRole


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email         = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name    = Column(String(100), nullable=False)
    last_name     = Column(String(100), nullable=False)
    role          = Column(SAEnum(UserRole), nullable=False, default=UserRole.buyer)
    is_active          = Column(Boolean, default=True,  nullable=False)
    is_email_verified  = Column(Boolean, default=False, nullable=False)

    # Путь к аватару в MinIO: avatars/{uuid}.jpg
    # URL генерируется на лету через minio_service.get_presigned_url()
    avatar_object_name = Column(String(500), nullable=True)

    # ── Связи ────────────────────────────────────────────────────────────────
    buyer_profile  = relationship("BuyerProfile",  back_populates="user", uselist=False)
    seller_profile = relationship("SellerProfile", back_populates="user", uselist=False)
    locations      = relationship("Location", back_populates="seller")
    bookings       = relationship("Booking",  back_populates="buyer")
    reviews        = relationship("Review",   back_populates="author")
    notifications  = relationship("Notification", back_populates="user")
    photos         = relationship("Photo",    back_populates="uploader")
