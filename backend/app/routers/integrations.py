"""OAuth integration endpoints for Microsoft 365 and Google Workspace."""

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.middleware.auth import get_current_tenant_id
from app.models.tenant import Tenant

router = APIRouter(prefix="/api/integrations", tags=["integrations"])
settings = get_settings()

# In production use Redis for OAuth state storage
_oauth_states: dict[str, dict] = {}


@router.get("/status")
async def integration_status(
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return which integrations are currently connected."""
    tid = uuid.UUID(tenant_id)
    result = await db.execute(select(Tenant).where(Tenant.id == tid))
    tenant = result.scalar_one_or_none()

    if not tenant:
        return {"microsoft365": False, "google": False}

    return {
        "microsoft365": {
            "connected": tenant.microsoft_connected,
            "tenant_id": tenant.microsoft_tenant_id,
            "last_sync": tenant.last_sync_at,
            "configured": settings.microsoft_configured,
        },
        "google": {
            "connected": tenant.google_connected,
            "domain": tenant.google_domain,
            "last_sync": tenant.last_sync_at,
            "configured": settings.google_configured,
        },
    }


@router.get("/microsoft/authorize")
async def microsoft_authorize(
    tenant_id: str = Depends(get_current_tenant_id),
) -> dict:
    """Generate a Microsoft OAuth2 authorization URL."""
    if not settings.microsoft_configured:
        raise HTTPException(
            status_code=400,
            detail="Microsoft 365 integration is not configured. Set MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET.",
        )

    state = secrets.token_urlsafe(32)
    _oauth_states[state] = {"tenant_id": tenant_id, "provider": "microsoft"}

    from app.services.microsoft_graph import get_authorization_url

    auth_url = get_authorization_url(state)
    return {"authorization_url": auth_url, "state": state}


@router.get("/microsoft/callback")
async def microsoft_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """Handle Microsoft OAuth2 callback and store tokens."""
    state_data = _oauth_states.pop(state, None)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    from app.services.microsoft_graph import exchange_code_for_token

    try:
        token_data = await exchange_code_for_token(code)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {exc}")

    tid = uuid.UUID(state_data["tenant_id"])
    result = await db.execute(select(Tenant).where(Tenant.id == tid))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant.microsoft_access_token = token_data.get("access_token")
    tenant.microsoft_refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 3600)
    tenant.microsoft_token_expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=expires_in
    )

    await db.commit()
    return RedirectResponse(url=f"{settings.frontend_url}/settings/integrations?connected=microsoft")


@router.delete("/microsoft/disconnect")
async def microsoft_disconnect(
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Remove Microsoft 365 integration tokens."""
    tid = uuid.UUID(tenant_id)
    result = await db.execute(select(Tenant).where(Tenant.id == tid))
    tenant = result.scalar_one_or_none()
    if tenant:
        tenant.microsoft_access_token = None
        tenant.microsoft_refresh_token = None
        tenant.microsoft_token_expires_at = None
        tenant.microsoft_tenant_id = None
        await db.commit()
    return {"status": "disconnected"}


@router.get("/google/authorize")
async def google_authorize(
    tenant_id: str = Depends(get_current_tenant_id),
) -> dict:
    """Generate a Google OAuth2 authorization URL."""
    if not settings.google_configured:
        raise HTTPException(
            status_code=400,
            detail="Google integration is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.",
        )

    state = secrets.token_urlsafe(32)
    _oauth_states[state] = {"tenant_id": tenant_id, "provider": "google"}

    from app.services.google_admin import get_authorization_url

    auth_url = get_authorization_url(state)
    return {"authorization_url": auth_url, "state": state}


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """Handle Google OAuth2 callback and store tokens."""
    state_data = _oauth_states.pop(state, None)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    from app.services.google_admin import exchange_code_for_token

    try:
        token_data = await exchange_code_for_token(code)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {exc}")

    tid = uuid.UUID(state_data["tenant_id"])
    result = await db.execute(select(Tenant).where(Tenant.id == tid))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    import json

    tenant.google_credentials = json.dumps(token_data)
    await db.commit()
    return RedirectResponse(url=f"{settings.frontend_url}/settings/integrations?connected=google")


@router.delete("/google/disconnect")
async def google_disconnect(
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Remove Google Workspace integration credentials."""
    tid = uuid.UUID(tenant_id)
    result = await db.execute(select(Tenant).where(Tenant.id == tid))
    tenant = result.scalar_one_or_none()
    if tenant:
        tenant.google_credentials = None
        tenant.google_domain = None
        await db.commit()
    return {"status": "disconnected"}
