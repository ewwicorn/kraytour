from datetime import datetime, timedelta
import hmac
import secrets
from typing import Set

from jose import JWTError, jwt

from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BLACKLISTED_TOKENS: Set[str] = set()

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt.

    Args:
        password: The plaintext password to hash.

    Returns:
        The hashed password string.
    """
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against its hash.

    Args:
        plain: The plaintext password to verify.
        hashed: The hashed password to compare against.

    Returns:
        True if password matches, False otherwise.
    """
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    """Create a JWT access token.

    Args:
        data: Dictionary containing token claims.

    Returns:
        Encoded JWT token string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT access token.

    Args:
        token: The JWT token string to decode.

    Returns:
        Dictionary containing decoded token claims.
    """
    decoded_jwt = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return decoded_jwt

def blacklist_token(token: str) -> None:
    """Add token to blacklist on logout.

    Args:
        token: The JWT token to blacklist.
    """
    BLACKLISTED_TOKENS.add(token)

def is_token_blacklisted(token: str) -> bool:
    """Check if token has been revoked.

    Args:
        token: The JWT token to check.

    Returns:
        True if token is blacklisted, False otherwise.
    """
    return token in BLACKLISTED_TOKENS

def generate_csrf_token() -> str:
    """Generate a cryptographically secure CSRF token.

    Returns:
        A random URL-safe token string.
    """
    return secrets.token_urlsafe(32)

def validate_csrf_token(token: str, session_token: str) -> bool:
    """Validate CSRF token using constant-time comparison.

    Args:
        token: The CSRF token to validate.
        session_token: The expected session token.

    Returns:
        True if tokens match, False otherwise.
    """
    return hmac.compare_digest(token, session_token)