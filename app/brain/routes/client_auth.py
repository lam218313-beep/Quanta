"""
Client Auth Bridge — Quanta

Lets a cliente log into Quanta with the SAME RUC + Clave SOL they use on
SUNAT, instead of a separate email/password. Supabase Auth has no native
"RUC + password" login mode, so this bridges it: verify the RUC/clave_sol
pair against `clientes`, then provision (or sync) a "shadow" Supabase Auth
account for that client (synthetic email, password kept in lockstep with
their current clave_sol on every login) and sign them in normally to
return a real session — the frontend hydrates it with `setSession(...)`
exactly as if the user had logged in with email/password directly.

Security note: this intentionally reuses the SUNAT portal password as the
Quanta login password (explicit product decision). `clientes.clave_sol` is
the single source of truth — if it changes, the shadow account's password
is re-synced on the next login attempt.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.brain.db.supabase_client import get_supabase
from app.brain.config import get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


class ClientLoginRequest(BaseModel):
    ruc: str
    clave_sol: str


def _synthetic_email(ruc: str) -> str:
    return f"{ruc}@clientes.quanta.internal"


def _auth_password(clave_sol: str) -> str:
    """
    Supabase Auth requires passwords of at least 6 characters, but SUNAT's
    Clave SOL has no such minimum — some real clients have shorter ones.
    Deterministically pad it so Supabase accepts it. The actual security
    check (exact match against clientes.clave_sol) happens before this is
    ever used, so the padding is just internal plumbing, never shown or
    typed by the user.
    """
    if len(clave_sol) >= 6:
        return clave_sol
    return (clave_sol + "_qSOL#2026")[:6]


@router.post("/client-login")
async def client_login(req: ClientLoginRequest):
    """Authenticate a cliente with RUC + Clave SOL and return a Supabase session."""
    supabase = get_supabase()  # service_role client — needed to read clientes/verify + admin-provision

    cliente_res = supabase.table("clientes").select("*").eq("ruc", req.ruc).execute()
    if not cliente_res.data:
        raise HTTPException(401, "RUC o clave SOL incorrectos")

    cliente = cliente_res.data[0]

    if not cliente.get("activo", True):
        raise HTTPException(403, "Este cliente está desactivado. Contacta a tu contador.")

    if cliente.get("clave_sol") != req.clave_sol:
        raise HTTPException(401, "RUC o clave SOL incorrectos")

    email = _synthetic_email(req.ruc)
    auth_password = _auth_password(req.clave_sol)

    profile_res = supabase.table("user_profiles") \
        .select("id, activo") \
        .eq("cliente_id", cliente["id"]) \
        .eq("role", "client") \
        .execute()

    try:
        if profile_res.data:
            user_id = profile_res.data[0]["id"]
            if not profile_res.data[0].get("activo", True):
                raise HTTPException(403, "Tu acceso a Quanta fue desactivado. Contacta a tu contador.")
            # Keep the shadow account's password in sync with the current clave_sol.
            supabase.auth.admin.update_user_by_id(user_id, {"password": auth_password})
        else:
            auth_res = supabase.auth.admin.create_user({
                "email": email,
                "password": auth_password,
                "email_confirm": True,
            })
            if not auth_res or not auth_res.user:
                raise HTTPException(500, "No se pudo crear el acceso del cliente")
            user_id = auth_res.user.id
            supabase.table("user_profiles").insert({
                "id": user_id,
                "email": email,
                "nombre": cliente.get("razon_social"),
                "role": "client",
                "cliente_id": cliente["id"],
                "activo": True,
            }).execute()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error preparando el acceso: {str(e)}")

    # Sign in through a plain (anon-key) client — same path the frontend would
    # take — so we hand back a real, normal Supabase session.
    settings = get_settings()
    try:
        from supabase import create_client
        anon_client = create_client(settings.supabase_url, settings.supabase_anon_key)
        session_res = anon_client.auth.sign_in_with_password({
            "email": email,
            "password": auth_password,
        })
    except Exception as e:
        raise HTTPException(500, f"Error iniciando sesión: {str(e)}")

    if not session_res or not session_res.session:
        raise HTTPException(500, "No se pudo iniciar sesión")

    session = session_res.session
    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "expires_at": session.expires_at,
        "cliente": {
            "id": cliente["id"],
            "ruc": cliente["ruc"],
            "razon_social": cliente["razon_social"],
        },
    }
