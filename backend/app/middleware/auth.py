"""JWT authentication middleware and helpers."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

security = HTTPBearer(auto_error=False)

# Demo tenant ID used when no auth is provided (development mode)
DEMO_TENANT_ID = "00000000-0000-0000-0000-000000000001"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


async def get_current_tenant_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """
    Extract tenant_id from JWT bearer token.
    In development mode without a token, returns the demo tenant ID.
    """
    if credentials is None:
        # Allow unauthenticated access to demo data in development
        if settings.environment == "development":
            return DEMO_TENANT_ID
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(credentials.credentials)
        tenant_id: Optional[str] = payload.get("tenant_id")
        if tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing tenant_id",
            )
        return tenant_id
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )
