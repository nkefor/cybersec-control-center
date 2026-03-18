"""Microsoft Graph API client for syncing users and sign-in data."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import urlencode

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
SCOPES = [
    "User.Read.All",
    "AuditLog.Read.All",
    "UserAuthenticationMethod.Read.All",
    "IdentityRiskyUser.Read.All",
    "Reports.Read.All",
    "offline_access",
]


def get_authorization_url(state: str) -> str:
    """Build the Azure AD OAuth2 authorization URL."""
    tenant_id = settings.microsoft_tenant_id or "common"
    params = {
        "client_id": settings.microsoft_client_id,
        "response_type": "code",
        "redirect_uri": settings.microsoft_redirect_uri,
        "scope": " ".join(SCOPES),
        "state": state,
        "response_mode": "query",
    }
    return f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize?{urlencode(params)}"


async def exchange_code_for_token(code: str) -> dict:
    """Exchange authorization code for access/refresh tokens."""
    tenant_id = settings.microsoft_tenant_id or "common"
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": settings.microsoft_client_id,
        "client_secret": settings.microsoft_client_secret,
        "code": code,
        "redirect_uri": settings.microsoft_redirect_uri,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)
        response.raise_for_status()
        return response.json()


async def refresh_access_token(refresh_token: str) -> dict:
    """Refresh an expired access token."""
    tenant_id = settings.microsoft_tenant_id or "common"
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": settings.microsoft_client_id,
        "client_secret": settings.microsoft_client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)
        response.raise_for_status()
        return response.json()


class MicrosoftGraphService:
    """Wrapper around Microsoft Graph API calls."""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def _get(self, path: str, params: Optional[dict] = None) -> Any:
        url = f"{GRAPH_BASE}{path}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=self.headers, params=params or {})
            if response.status_code == 401:
                raise ValueError("Microsoft Graph token expired or invalid")
            response.raise_for_status()
            return response.json()

    async def get_users_with_mfa(self) -> list[dict]:
        """
        Fetch all users and their MFA registration details.
        Combines /users with /reports/authenticationMethods/userRegistrationDetails.
        """
        try:
            # Fetch user registration details (MFA methods)
            reg_data = await self._get(
                "/reports/authenticationMethods/userRegistrationDetails",
                params={"$select": "id,userPrincipalName,isMfaRegistered,methodsRegistered"},
            )
            mfa_by_id = {
                u["id"]: u for u in reg_data.get("value", [])
            }

            # Fetch users list
            users_data = await self._get(
                "/users",
                params={
                    "$select": "id,displayName,userPrincipalName,accountEnabled,signInActivity",
                    "$top": "999",
                },
            )

            result = []
            for user in users_data.get("value", []):
                uid = user["id"]
                reg = mfa_by_id.get(uid, {})
                last_sign = user.get("signInActivity", {})
                last_sign_at = None
                if last_sign.get("lastSignInDateTime"):
                    last_sign_at = datetime.fromisoformat(
                        last_sign["lastSignInDateTime"].replace("Z", "+00:00")
                    )
                result.append(
                    {
                        "external_id": uid,
                        "email": user.get("userPrincipalName", ""),
                        "display_name": user.get("displayName", ""),
                        "is_active": user.get("accountEnabled", True),
                        "mfa_enabled": reg.get("isMfaRegistered", False),
                        "mfa_methods": reg.get("methodsRegistered", []),
                        "last_sign_in": last_sign_at,
                    }
                )
            return result
        except Exception as exc:
            logger.error("Error fetching Microsoft users: %s", exc)
            return []

    async def get_risky_sign_ins(self) -> list[dict]:
        """Fetch risky sign-in events from Identity Protection."""
        try:
            data = await self._get(
                "/identityProtection/riskySignIns",
                params={
                    "$select": "id,userId,userDisplayName,userPrincipalName,riskLevel,riskState,riskDetail,createdDateTime,ipAddress,location",
                    "$top": "50",
                    "$filter": "riskState eq 'atRisk' or riskState eq 'confirmedCompromised'",
                },
            )
            return data.get("value", [])
        except Exception as exc:
            logger.warning("Could not fetch risky sign-ins (may need P2 license): %s", exc)
            return []

    async def get_devices(self) -> list[dict]:
        """Fetch managed devices from Graph."""
        try:
            data = await self._get(
                "/devices",
                params={
                    "$select": "id,displayName,operatingSystem,operatingSystemVersion,isCompliant,isManaged,approximateLastSignInDateTime",
                    "$top": "999",
                },
            )
            return data.get("value", [])
        except Exception as exc:
            logger.error("Error fetching Microsoft devices: %s", exc)
            return []
