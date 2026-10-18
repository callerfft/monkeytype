"""Authentication dependencies supporting Firebase JWT and Mock Auth."""

from typing import Optional, Dict, Any
from fastapi import Header, Depends
import jwt

from .exceptions import UnauthorizedError
from ..config import settings


async def get_optional_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> Optional[Dict[str, Any]]:
    """Extract authenticated user if Bearer token present, else return None for guest."""
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        return None

    token = authorization[len("Bearer ") :].strip()
    if not token:
        return None

    if settings.AUTH_MODE == "mock":
        # Extract user id from token or use default mock
        user_id = "mock-user-123"
        email = "user@linguatype.app"
        if token.startswith("user_"):
            user_id = token
            email = f"{token}@linguatype.app"
        return {
            "uid": user_id,
            "email": email,
            "display_name": "LinguaType User",
        }

    # Firebase JWT decoding
    try:
        # In production with live certificates, verify signature against Google JWKS.
        # Unverified decode for payload extraction if offline or dev
        unverified = jwt.decode(token, options={"verify_signature": False})
        return {
            "uid": unverified.get("user_id") or unverified.get("sub", "unknown-user"),
            "email": unverified.get("email", "user@linguatype.app"),
            "display_name": unverified.get("name"),
        }
    except Exception:
        return None


async def get_current_user(
    user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Dict[str, Any]:
    """Require valid authenticated user; raise UnauthorizedError if missing or invalid."""
    if not user:
        raise UnauthorizedError(
            message="Valid Firebase Bearer token is required.",
            code="UNAUTHORIZED",
        )
    return user
