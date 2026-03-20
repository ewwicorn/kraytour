"""
core/enums.py — все перечисления проекта.

Сгруппированы по смыслу: пользователи, модерация,
бронирования, медиа, уведомления.
"""
import enum


# ── Пользователи ──────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    buyer  = "buyer"
    seller = "seller"
    admin  = "admin"


# ── Контент и модерация ───────────────────────────────────────────────────────

class EntityType(str, enum.Enum):
    """Тип сущности: локация или событие."""
    location = "location"
    event    = "event"


class ModerationStatus(str, enum.Enum):
    """
    Жизненный цикл контента (локации, события, отзыва, баннера):
    draft → pending → approved / rejected / edit_requested
    """
    draft          = "draft"
    pending        = "pending"
    approved       = "approved"
    rejected       = "rejected"
    edit_requested = "edit_requested"


# ── Туры ──────────────────────────────────────────────────────────────────────

class TourStatus(str, enum.Enum):
    draft  = "draft"   # собирается в конструкторе
    booked = "booked"  # все остановки забронированы


# ── Бронирования и платежи ────────────────────────────────────────────────────

class BookingStatus(str, enum.Enum):
    pending   = "pending"    # создана, ожидает оплаты
    confirmed = "confirmed"  # продавец подтвердил
    completed = "completed"  # визит состоялся
    cancelled = "cancelled"  # отменена


class PaymentStatus(str, enum.Enum):
    pending   = "pending"    # создан, ожидает оплаты на стороне ЮKassa
    succeeded = "succeeded"  # оплачен
    cancelled = "cancelled"  # отменён
    refunded  = "refunded"   # возврат выполнен


# ── Медиа ─────────────────────────────────────────────────────────────────────

class VideoStatus(str, enum.Enum):
    """
    Жизненный цикл генерации видео из фото:
    pending → processing → done / error
    """
    pending    = "pending"     # задача создана, ещё не взята в работу
    processing = "processing"  # генерация идёт
    done       = "done"        # видео готово, object_name заполнен
    error      = "error"       # ошибка, см. error_message


# ── Уведомления ───────────────────────────────────────────────────────────────

class NotificationType(str, enum.Enum):
    booking_confirmed    = "booking_confirmed"
    booking_cancelled    = "booking_cancelled"
    booking_reminder     = "booking_reminder"
    moderation_approved  = "moderation_approved"
    moderation_rejected  = "moderation_rejected"
    new_review           = "new_review"
    new_message          = "new_message"
