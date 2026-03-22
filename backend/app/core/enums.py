"""Enumeration types for user roles, entities, and content moderation."""

import enum

class UserRole(str, enum.Enum):
    """User account role in the system."""

    buyer  = "buyer"
    seller = "seller"
    admin  = "admin"

class EntityType(str, enum.Enum):
    """Platform content entity types."""

    location = "location"
    event    = "event"


class ModerationStatus(str, enum.Enum):
    """Content lifecycle status in moderation workflow.

    States: draft → pending → approved/rejected/edit_requested
    """
    draft          = "draft"
    pending        = "pending"
    approved       = "approved"
    rejected       = "rejected"
    edit_requested = "edit_requested"

class TourStatus(str, enum.Enum):
    draft  = "draft"
    booked = "booked"
    
class BookingStatus(str, enum.Enum):
    pending   = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"


class PaymentStatus(str, enum.Enum):
    pending   = "pending"
    succeeded = "succeeded"
    cancelled = "cancelled"
    refunded  = "refunded"

class VideoStatus(str, enum.Enum):
    pending    = "pending"
    processing = "processing"
    done       = "done"
    error      = "error"

class NotificationType(str, enum.Enum):
    booking_confirmed    = "booking_confirmed"
    booking_cancelled    = "booking_cancelled"
    booking_reminder     = "booking_reminder"
    moderation_approved  = "moderation_approved"
    moderation_rejected  = "moderation_rejected"
    new_review           = "new_review"
    new_message          = "new_message"
