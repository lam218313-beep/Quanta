"""
Auth Middleware — Quanta V2

Extracts and verifies JWT tokens from incoming requests.
Injects `user_id`, `role`, and `cliente_id` into the request state
so that downstream endpoints can use them for authorization.

The backend uses the Supabase service_role key for DB operations
(bypassing RLS), but the middleware validates the USER's token
to determine their permissions.

Usage in endpoints:
    from app.brain.middleware.auth import require_role, get_current_user

    @router.get("/protected")
    async def protected_endpoint(user = Depends(get_current_user)):
        # user.role, user.user_id, user.cliente_id
        ...

    @router.get("/admin-only")
    async def admin_endpoint(user = Depends(require_role("admin"))):
        ...
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Ensure we can import app modules
_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    """Represents the current authenticated user."""
    user_id: str
    role: str  # "admin", "accountant", "client"
    cliente_id: Optional[str]  # UUID of the client they belong to (None for admins)
    email: str


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> AuthenticatedUser:
    """
    FastAPI dependency that extracts and validates the JWT from the
    Authorization header.  Returns an AuthenticatedUser or raises 401.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Token de autenticación requerido")

    token = credentials.credentials

    try:
        from app.brain.db.supabase_client import get_supabase
        supabase = get_supabase()

        # Verify the JWT with Supabase Auth
        user_response = supabase.auth.get_user(token)

        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")

        auth_user = user_response.user
        user_id = auth_user.id

        # Look up the user's profile for role and cliente_id
        profile_res = supabase.table("user_profiles") \
            .select("role, cliente_id, email, activo") \
            .eq("id", user_id) \
            .execute()

        if not profile_res.data:
            # User exists in auth but has no profile — default to client role
            return AuthenticatedUser(
                user_id=user_id,
                role="client",
                cliente_id=None,
                email=auth_user.email or "",
            )

        profile = profile_res.data[0]

        if not profile.get("activo", True):
            raise HTTPException(status_code=403, detail="Usuario desactivado")

        return AuthenticatedUser(
            user_id=user_id,
            role=profile.get("role", "client"),
            cliente_id=profile.get("cliente_id"),
            email=profile.get("email", auth_user.email or ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Error de autenticación: {str(e)}")


def require_role(*allowed_roles: str):
    """
    Factory that returns a FastAPI dependency requiring specific role(s).

    Usage:
        @router.get("/admin-only")
        async def endpoint(user = Depends(require_role("admin"))):
            ...

        @router.get("/staff")
        async def endpoint(user = Depends(require_role("admin", "accountant"))):
            ...
    """
    async def _check_role(user: AuthenticatedUser = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Acceso denegado. Rol requerido: {', '.join(allowed_roles)}. Tu rol: {user.role}",
            )
        return user

    return _check_role


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> Optional[AuthenticatedUser]:
    """
    Like get_current_user but returns None instead of raising 401
    when no token is provided.  Useful for endpoints that work
    differently for authenticated vs anonymous users.
    """
    if not credentials:
        return None
    try:
        import asyncio
        # This is a sync wrapper; for async contexts, use get_current_user directly
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return None  # Can't await in sync context
        return loop.run_until_complete(get_current_user(None, credentials))
    except Exception:
        return None
