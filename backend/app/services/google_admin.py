"""Google Workspace Admin SDK client."""

import json
import logging
from typing import Any, Optional
from urllib.parse import urlencode

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
ADMIN_BASE = "https://admin.googleapis.com/admin/directory/v1"
REPORTS_BASE = "https://admin.googleapis.com/admin/reports/v1"

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user.readonly",
    "https://www.googleapis.com/auth/admin.reports.audit.readonly",
    "https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly",
]


def get_authorization_url(state: str) -> str:
    """Build the Google OAuth2 authorization URL."""
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


async def exchange_code_for_token(code: str) -> dict:
    """Exchange code for Google tokens."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        response.raise_for_status()
        return response.json()


async def refresh_access_token(refresh_token: str) -> dict:
    """Refresh Google access token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "refresh_token": refresh_token,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "grant_type": "refresh_token",
            },
        )
        response.raise_for_status()
        return response.json()


class GoogleAdminService:
    """Wrapper around Google Admin SDK calls."""

    def __init__(self, credentials: dict):
        self.credentials = credentials
        self.access_token = credentials.get("access_token", "")

    async def _get(self, base: str, path: str, params: Optional[dict] = None) -> Any:
        url = f"{base}{path}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=headers, params=params or {})
            if response.status_code == 401:
                raise ValueError("Google token expired or invalid")
            response.raise_for_status()
            return response.json()

    async def get_users(self, domain: str) -> list[dict]:
        """Fetch all users in a Google Workspace domain."""
        try:
            data = await self._get(
                ADMIN_BASE,
                "/users",
                params={
                    "domain": domain,
                    "maxResults": 500,
                    "projection": "full",
                },
            )
            users = data.get("users", [])
            result = []
            for u in users:
                name = u.get("name", {})
                mfa_enrolled = u.get("isEnrolledIn2Sv", False)
                last_login = u.get("lastLoginTime")

                from datetime import datetime

                last_sign_in = None
                if last_login and last_login != "1970-01-01T00:00:00.000Z":
                    try:
                        last_sign_in = datetime.fromisoformat(last_login.replace("Z", "+00:00"))
                    except ValueError:
                        pass

                result.append(
                    {
                        "external_id": u.get("id"),
                        "email": u.get("primaryEmail", ""),
                        "display_name": name.get("fullName", ""),
                        "is_active": not u.get("suspended", False),
                        "mfa_enabled": mfa_enrolled,
                        "mfa_methods": ["totp"] if mfa_enrolled else [],
                        "last_sign_in": last_sign_in,
                    }
                )
            return result
        except Exception as exc:
            logger.error("Error fetching Google users: %s", exc)
            return []

    async def get_login_activity(self, domain: str) -> list[dict]:
        """Fetch login audit events for suspicious activity detection."""
        try:
            data = await self._get(
                REPORTS_BASE,
                "/activity/users/all/applications/login",
                params={
                    "maxResults": 100,
                    "eventName": "login_failure",
                },
            )
            return data.get("items", [])
        except Exception as exc:
            logger.warning("Could not fetch Google login activity: %s", exc)
            return []
