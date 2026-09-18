"""
User Management Routes — Quanta V2

Admin-only endpoints for creating, listing, updating, and deactivating users.
Uses Supabase Auth for account creation and user_profiles for role management.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.brain.db.supabase_client import get_supabase
from app.brain.middleware.auth import require_role, AuthenticatedUser

router = APIRouter(prefix="/api/users", tags=["users"])


# ── Request/Response Models ──────────────────────────────────────

class CreateUserRequest(BaseModel):
    email: str
    password: str
    nombre: str
    role: str = "client"  # "admin", "accountant", "client"
    cliente_id: Optional[str] = None  # UUID — required for "client" role
    ruc: Optional[str] = None  # Alternative: resolve cliente_id from RUC


class UpdateUserRequest(BaseModel):
    nombre: Optional[str] = None
    role: Optional[str] = None
    cliente_id: Optional[str] = None
    activo: Optional[bool] = None


# ── Endpoints ────────────────────────────────────────────────────

@router.post("")
async def create_user(
    req: CreateUserRequest,
    admin: AuthenticatedUser = Depends(require_role("admin")),
):
    """Create a new user (admin only). Creates Supabase Auth account + profile."""
    supabase = get_supabase()

    # Validate role
    if req.role not in ("admin", "accountant", "client"):
        raise HTTPException(400, "Rol inválido. Opciones: admin, accountant, client")

    # Resolve cliente_id from RUC if provided
    cliente_id = req.cliente_id
    if not cliente_id and req.ruc:
        res = supabase.table("clientes").select("id").eq("ruc", req.ruc).execute()
        if not res.data:
            raise HTTPException(404, f"Cliente con RUC {req.ruc} no encontrado")
        cliente_id = res.data[0]["id"]

    if req.role == "client" and not cliente_id:
        raise HTTPException(400, "El rol 'client' requiere un cliente_id o ruc")

    try:
        # 1. Create user in Supabase Auth
        auth_response = supabase.auth.admin.create_user({
            "email": req.email,
            "password": req.password,
            "email_confirm": True,  # Auto-confirm for admin-created users
        })

        if not auth_response or not auth_response.user:
            raise HTTPException(500, "Error creando usuario en Supabase Auth")

        user_id = auth_response.user.id

        # 2. Create profile
        supabase.table("user_profiles").insert({
            "id": user_id,
            "email": req.email,
            "nombre": req.nombre,
            "role": req.role,
            "cliente_id": cliente_id,
            "activo": True,
        }).execute()

        return {
            "ok": True,
            "user_id": user_id,
            "email": req.email,
            "role": req.role,
            "cliente_id": cliente_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error creando usuario: {str(e)}")


@router.get("")
async def list_users(
    admin: AuthenticatedUser = Depends(require_role("admin")),
):
    """List all users (admin only)."""
    supabase = get_supabase()

    res = supabase.table("user_profiles") \
        .select("id, email, nombre, role, cliente_id, activo, created_at, clientes(ruc, razon_social)") \
        .order("created_at", desc=True) \
        .execute()

    users = []
    for u in (res.data or []):
        cliente_info = u.get("clientes")
        users.append({
            "id": u["id"],
            "email": u["email"],
            "nombre": u.get("nombre"),
            "role": u["role"],
            "activo": u["activo"],
            "cliente_id": u.get("cliente_id"),
            "cliente_ruc": cliente_info.get("ruc") if cliente_info else None,
            "cliente_razon_social": cliente_info.get("razon_social") if cliente_info else None,
            "created_at": u.get("created_at"),
        })

    return {"users": users, "total": len(users)}


@router.patch("/{user_id}")
async def update_user(
    user_id: str,
    req: UpdateUserRequest,
    admin: AuthenticatedUser = Depends(require_role("admin")),
):
    """Update a user's profile (admin only)."""
    supabase = get_supabase()

    # Check user exists
    check = supabase.table("user_profiles").select("id").eq("id", user_id).execute()
    if not check.data:
        raise HTTPException(404, "Usuario no encontrado")

    update_data = {}
    if req.nombre is not None:
        update_data["nombre"] = req.nombre
    if req.role is not None:
        if req.role not in ("admin", "accountant", "client"):
            raise HTTPException(400, "Rol inválido")
        update_data["role"] = req.role
    if req.cliente_id is not None:
        update_data["cliente_id"] = req.cliente_id
    if req.activo is not None:
        update_data["activo"] = req.activo

    if not update_data:
        raise HTTPException(400, "No hay campos para actualizar")

    supabase.table("user_profiles").update(update_data).eq("id", user_id).execute()

    return {"ok": True, "id": user_id, "updated": update_data}


@router.delete("/{user_id}")
async def deactivate_user(
    user_id: str,
    admin: AuthenticatedUser = Depends(require_role("admin")),
):
    """Deactivate a user (soft delete — admin only)."""
    supabase = get_supabase()

    check = supabase.table("user_profiles").select("id").eq("id", user_id).execute()
    if not check.data:
        raise HTTPException(404, "Usuario no encontrado")

    # Prevent admin from deactivating themselves
    if user_id == admin.user_id:
        raise HTTPException(400, "No puedes desactivar tu propia cuenta")

    supabase.table("user_profiles") \
        .update({"activo": False}) \
        .eq("id", user_id) \
        .execute()

    return {"ok": True, "id": user_id, "message": "Usuario desactivado"}


@router.get("/me")
async def get_current_user_profile(
    user: AuthenticatedUser = Depends(require_role("admin", "accountant", "client")),
):
    """Get the current authenticated user's profile."""
    supabase = get_supabase()

    res = supabase.table("user_profiles") \
        .select("*, clientes(ruc, razon_social)") \
        .eq("id", user.user_id) \
        .execute()

    if not res.data:
        return {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role,
            "profile_exists": False,
        }

    profile = res.data[0]
    cliente = profile.get("clientes")

    return {
        "user_id": user.user_id,
        "email": profile.get("email"),
        "nombre": profile.get("nombre"),
        "role": profile.get("role"),
        "activo": profile.get("activo"),
        "cliente_id": profile.get("cliente_id"),
        "cliente_ruc": cliente.get("ruc") if cliente else None,
        "cliente_razon_social": cliente.get("razon_social") if cliente else None,
        "profile_exists": True,
    }
