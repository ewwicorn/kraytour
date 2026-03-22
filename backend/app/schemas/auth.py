from pydantic import BaseModel, EmailStr, field_validator

from uuid import UUID

from app.core.enums import UserRole

class RegisterRequest(BaseModel):
    """User registration request schema."""

    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.buyer
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Minimum password requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
    
class LoginRequest(BaseModel):
    """User login request schema."""

    email: EmailStr
    password: str
    
class TokenResponse(BaseModel):
    """JWT token response schema."""

    access_token: str
    token_type: str = "bearer"
    
class UserOut(BaseModel):
    """User profile response schema."""

    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    
    class Config:
        from_attributes = True