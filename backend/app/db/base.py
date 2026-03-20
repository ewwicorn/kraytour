"""
db/base.py — декларативная база и общий миксин.

TimestampMixin добавляет created_at во все модели,
чтобы не повторять одно и то же поле в каждом файле.
"""
import uuid

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class UUIDMixin:
    """UUID первичный ключ — подключается ко всем моделям."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    """Поле created_at — подключается туда, где нужна дата создания."""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class FullTimestampMixin(TimestampMixin):
    """created_at + updated_at — для моделей, которые часто обновляются."""
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
