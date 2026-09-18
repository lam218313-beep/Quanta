"""
Dashboard API Routes — Quanta V2

RESTful endpoints for client dashboards.
Each endpoint receives a cliente_id and returns structured data
for standard accounting views and Quanta-specific categorizations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.brain.db.supabase_client import get_supabase
from app.brain.services.dashboard_service import (
    get_resumen_mensual,
    get_libro_compras,
    get_libro_ventas,
    get_liquidacion,
    get_completitud,
    get_tipificaciones,
    get_libro_diario,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _resolve_cliente_id(ruc: str) -> str:
    """Resolve a RUC to a cliente_id UUID. Raises 404 if not found."""
    supabase = get_supabase()
    res = supabase.table("clientes").select("id").eq("ruc", ruc).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail=f"Cliente con RUC {ruc} no encontrado")
    return res.data[0]["id"]


# ── Helper: accept either cliente_id or ruc ──────────────────────

def _get_cliente_id(cliente_id: Optional[str], ruc: Optional[str]) -> str:
    if cliente_id:
        return cliente_id
    if ruc:
        return _resolve_cliente_id(ruc)
    raise HTTPException(status_code=400, detail="Debe proporcionar cliente_id o ruc")


# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@router.get("/{cliente_id}/resumen-mensual")
def dashboard_resumen_mensual(
    cliente_id: str,
    anio: str = Query(..., description="Año a consultar, ej: 2026"),
):
    """Resumen mensual de compras vs ventas para todo un año."""
    return get_resumen_mensual(cliente_id, anio)


@router.get("/{cliente_id}/libro-compras")
def dashboard_libro_compras(
    cliente_id: str,
    periodo: str = Query(..., description="Periodo YYYYMM"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
):
    """Libro de compras detallado con paginación."""
    return get_libro_compras(cliente_id, periodo, page, page_size)


@router.get("/{cliente_id}/libro-ventas")
def dashboard_libro_ventas(
    cliente_id: str,
    periodo: str = Query(..., description="Periodo YYYYMM"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
):
    """Libro de ventas detallado con paginación."""
    return get_libro_ventas(cliente_id, periodo, page, page_size)


@router.get("/{cliente_id}/libro-diario")
def dashboard_libro_diario(
    cliente_id: str,
    periodo: str = Query(..., description="Periodo YYYYMM"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
):
    """Vista unificada de compras y ventas (libro diario) con paginación."""
    return get_libro_diario(cliente_id, periodo, page, page_size)


@router.get("/{cliente_id}/liquidacion")
def dashboard_liquidacion(
    cliente_id: str,
    periodo: str = Query(..., description="Periodo YYYYMM"),
):
    """Liquidación de impuestos: IGV a pagar, Renta MYPE, crédito fiscal."""
    return get_liquidacion(cliente_id, periodo)


@router.get("/{cliente_id}/completitud")
def dashboard_completitud(
    cliente_id: str,
    periodo: str = Query(..., description="Periodo YYYYMM"),
):
    """Estado de completitud: % descarga XML, PDF, enriquecimiento, clasificación IA."""
    return get_completitud(cliente_id, periodo)


@router.get("/{cliente_id}/tipificaciones")
def dashboard_tipificaciones(
    cliente_id: str,
    periodo: str = Query(..., description="Periodo YYYYMM"),
):
    """Tipificaciones empresariales: categorización de gastos e ingresos por categoría y cuenta contable."""
    return get_tipificaciones(cliente_id, periodo)


# ── Convenience: lookup by RUC instead of UUID ───────────────────

@router.get("/by-ruc/{ruc}/resumen-mensual")
def dashboard_by_ruc_resumen(ruc: str, anio: str = Query(...)):
    return get_resumen_mensual(_resolve_cliente_id(ruc), anio)

@router.get("/by-ruc/{ruc}/libro-compras")
def dashboard_by_ruc_compras(ruc: str, periodo: str = Query(...), page: int = 1, page_size: int = 100):
    return get_libro_compras(_resolve_cliente_id(ruc), periodo, page, page_size)

@router.get("/by-ruc/{ruc}/libro-ventas")
def dashboard_by_ruc_ventas(ruc: str, periodo: str = Query(...), page: int = 1, page_size: int = 100):
    return get_libro_ventas(_resolve_cliente_id(ruc), periodo, page, page_size)

@router.get("/by-ruc/{ruc}/libro-diario")
def dashboard_by_ruc_diario(ruc: str, periodo: str = Query(...), page: int = 1, page_size: int = 100):
    return get_libro_diario(_resolve_cliente_id(ruc), periodo, page, page_size)

@router.get("/by-ruc/{ruc}/liquidacion")
def dashboard_by_ruc_liquidacion(ruc: str, periodo: str = Query(...)):
    return get_liquidacion(_resolve_cliente_id(ruc), periodo)

@router.get("/by-ruc/{ruc}/completitud")
def dashboard_by_ruc_completitud(ruc: str, periodo: str = Query(...)):
    return get_completitud(_resolve_cliente_id(ruc), periodo)

@router.get("/by-ruc/{ruc}/tipificaciones")
def dashboard_by_ruc_tipificaciones(ruc: str, periodo: str = Query(...)):
    return get_tipificaciones(_resolve_cliente_id(ruc), periodo)
