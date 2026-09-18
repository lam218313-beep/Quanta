"""
Dashboard Service — Quanta V2

Centralised data-access layer for client dashboards.
Queries the Supabase database and returns structured data ready
for consumption by API endpoints and (eventually) a frontend.

All methods accept a `cliente_id` (UUID) and a `periodo` (YYYYMM string)
and return plain dicts — no ORM models, keeping things simple.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# Ensure we can import app modules
_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.brain.db.supabase_client import get_supabase


def _safe_float(val) -> float:
    try:
        return float(val or 0)
    except (TypeError, ValueError):
        return 0.0


# ═══════════════════════════════════════════════════════════════════
# 1. RESUMEN MENSUAL
# ═══════════════════════════════════════════════════════════════════

def get_resumen_mensual(cliente_id: str, anio: str) -> list[dict]:
    """
    Monthly summary for a client across all months of a year.
    Returns a list of dicts with: periodo, total_compras, total_ventas,
    igv_compras, igv_ventas, utilidad_bruta, cantidad_compras, cantidad_ventas.
    """
    supabase = get_supabase()
    periodos = [f"{anio}{m:02d}" for m in range(1, 13)]
    results = []

    for periodo in periodos:
        # Compras
        res_c = supabase.table("sire_preliminar_compras") \
            .select("total_cp, igv_ipm_dg, bi_gravado_dg") \
            .eq("cliente_id", cliente_id) \
            .eq("periodo", periodo) \
            .execute()

        total_compras = sum(_safe_float(r["total_cp"]) for r in (res_c.data or []))
        igv_compras = sum(_safe_float(r["igv_ipm_dg"]) for r in (res_c.data or []))
        bi_compras = sum(_safe_float(r["bi_gravado_dg"]) for r in (res_c.data or []))
        cant_compras = len(res_c.data or [])

        # Ventas
        res_v = supabase.table("sire_preliminar_ventas") \
            .select("total_cp, igv_ipm, bi_gravada") \
            .eq("cliente_id", cliente_id) \
            .eq("periodo", periodo) \
            .execute()

        total_ventas = sum(_safe_float(r["total_cp"]) for r in (res_v.data or []))
        igv_ventas = sum(_safe_float(r["igv_ipm"]) for r in (res_v.data or []))
        bi_ventas = sum(_safe_float(r["bi_gravada"]) for r in (res_v.data or []))
        cant_ventas = len(res_v.data or [])

        if cant_compras > 0 or cant_ventas > 0:
            results.append({
                "periodo": periodo,
                "mes": int(periodo[4:]),
                "total_compras": round(total_compras, 2),
                "total_ventas": round(total_ventas, 2),
                "bi_compras": round(bi_compras, 2),
                "bi_ventas": round(bi_ventas, 2),
                "igv_compras": round(igv_compras, 2),
                "igv_ventas": round(igv_ventas, 2),
                "cantidad_compras": cant_compras,
                "cantidad_ventas": cant_ventas,
                "utilidad_bruta": round(total_ventas - total_compras, 2),
            })

    return results


# ═══════════════════════════════════════════════════════════════════
# 2. LIBRO DE COMPRAS
# ═══════════════════════════════════════════════════════════════════

def get_libro_compras(
    cliente_id: str,
    periodo: str,
    page: int = 1,
    page_size: int = 100,
) -> dict:
    """
    Paged list of purchases for a client/period.
    Includes enrichment and AI classification data.
    """
    supabase = get_supabase()
    offset = (page - 1) * page_size

    res = supabase.table("sire_preliminar_compras") \
        .select("*", count="exact") \
        .eq("cliente_id", cliente_id) \
        .eq("periodo", periodo) \
        .order("fecha_emision") \
        .range(offset, offset + page_size - 1) \
        .execute()

    return {
        "data": res.data or [],
        "total": res.count or 0,
        "page": page,
        "page_size": page_size,
    }


# ═══════════════════════════════════════════════════════════════════
# 3. LIBRO DE VENTAS
# ═══════════════════════════════════════════════════════════════════

def get_libro_ventas(
    cliente_id: str,
    periodo: str,
    page: int = 1,
    page_size: int = 100,
) -> dict:
    """Paged list of sales for a client/period."""
    supabase = get_supabase()
    offset = (page - 1) * page_size

    res = supabase.table("sire_preliminar_ventas") \
        .select("*", count="exact") \
        .eq("cliente_id", cliente_id) \
        .eq("periodo", periodo) \
        .order("fecha_emision") \
        .range(offset, offset + page_size - 1) \
        .execute()

    return {
        "data": res.data or [],
        "total": res.count or 0,
        "page": page,
        "page_size": page_size,
    }


# ═══════════════════════════════════════════════════════════════════
# 4. LIQUIDACIÓN DE IMPUESTOS
# ═══════════════════════════════════════════════════════════════════

def get_liquidacion(cliente_id: str, periodo: str) -> dict:
    """
    Tax settlement calculation for a period.
    Returns IGV ventas, IGV compras, crédito fiscal, IGV a pagar, Renta MYPE.
    """
    supabase = get_supabase()

    # Ventas
    res_v = supabase.table("sire_preliminar_ventas") \
        .select("total_cp, igv_ipm, bi_gravada, mto_exonerado, mto_inafecto") \
        .eq("cliente_id", cliente_id) \
        .eq("periodo", periodo) \
        .execute()

    total_ventas = sum(_safe_float(r["total_cp"]) for r in (res_v.data or []))
    igv_ventas = sum(_safe_float(r["igv_ipm"]) for r in (res_v.data or []))
    bi_ventas = sum(_safe_float(r["bi_gravada"]) for r in (res_v.data or []))

    # Compras
    res_c = supabase.table("sire_preliminar_compras") \
        .select("total_cp, igv_ipm_dg, bi_gravado_dg") \
        .eq("cliente_id", cliente_id) \
        .eq("periodo", periodo) \
        .execute()

    total_compras = sum(_safe_float(r["total_cp"]) for r in (res_c.data or []))
    igv_compras = sum(_safe_float(r["igv_ipm_dg"]) for r in (res_c.data or []))
    bi_compras = sum(_safe_float(r["bi_gravado_dg"]) for r in (res_c.data or []))

    igv_a_pagar = max(0, igv_ventas - igv_compras)
    renta_mype = total_ventas * 0.01
    total_a_pagar = igv_a_pagar + renta_mype
    utilidad = total_ventas - total_compras
    margen = (utilidad / total_ventas * 100) if total_ventas > 0 else 0

    return {
        "periodo": periodo,
        "ventas": {
            "total": round(total_ventas, 2),
            "base_imponible": round(bi_ventas, 2),
            "igv": round(igv_ventas, 2),
            "cantidad": len(res_v.data or []),
        },
        "compras": {
            "total": round(total_compras, 2),
            "base_imponible": round(bi_compras, 2),
            "igv": round(igv_compras, 2),
            "cantidad": len(res_c.data or []),
        },
        "liquidacion": {
            "igv_a_pagar": round(igv_a_pagar, 2),
            "credito_fiscal": round(igv_compras, 2),
            "renta_mype_1pct": round(renta_mype, 2),
            "total_a_pagar": round(total_a_pagar, 2),
        },
        "indicadores": {
            "utilidad_bruta": round(utilidad, 2),
            "margen_utilidad_pct": round(margen, 2),
        },
    }


# ═══════════════════════════════════════════════════════════════════
# 5. COMPLETITUD DE DESCARGA
# ═══════════════════════════════════════════════════════════════════

def get_completitud(cliente_id: str, periodo: str) -> dict:
    """
    Download/enrichment completeness for a client/period.
    Shows % of XMLs downloaded, PDFs generated, enriched, classified.
    """
    supabase = get_supabase()

    # Comprobantes físicos
    res = supabase.table("sire_comprobantes_fisicos") \
        .select("estado_xml, estado_pdf, tipo_libro") \
        .eq("cliente_id", cliente_id) \
        .eq("periodo", periodo) \
        .execute()

    records = res.data or []
    total = len(records)

    xml_ok = sum(1 for r in records if r["estado_xml"] == "DESCARGADO")
    pdf_ok = sum(1 for r in records if r["estado_pdf"] == "DESCARGADO")
    xml_pend = sum(1 for r in records if r["estado_xml"] in ("PENDIENTE", "ERROR"))
    pdf_pend = sum(1 for r in records if r["estado_pdf"] in ("PENDIENTE", "ERROR"))
    no_desc = sum(1 for r in records if r["estado_xml"] == "NO_DESCARGABLE")

    # Enrichment stats
    for libro, tabla in [("COMPRAS", "sire_preliminar_compras"), ("VENTAS", "sire_preliminar_ventas")]:
        pass  # We'll get these from the preliminar tables

    res_ec = supabase.table("sire_preliminar_compras") \
        .select("estado_enriquecimiento, cuenta_contable") \
        .eq("cliente_id", cliente_id) \
        .eq("periodo", periodo) \
        .execute()

    res_ev = supabase.table("sire_preliminar_ventas") \
        .select("estado_enriquecimiento, cuenta_contable") \
        .eq("cliente_id", cliente_id) \
        .eq("periodo", periodo) \
        .execute()

    all_prelim = (res_ec.data or []) + (res_ev.data or [])
    total_prelim = len(all_prelim)
    enriquecidos = sum(1 for r in all_prelim if r.get("estado_enriquecimiento") == "COMPLETO")
    clasificados = sum(1 for r in all_prelim if r.get("cuenta_contable"))

    return {
        "periodo": periodo,
        "comprobantes_fisicos": {
            "total": total,
            "xml_descargados": xml_ok,
            "xml_pendientes": xml_pend,
            "pdf_generados": pdf_ok,
            "pdf_pendientes": pdf_pend,
            "no_descargables": no_desc,
            "pct_xml": round(xml_ok / total * 100, 1) if total > 0 else 0,
            "pct_pdf": round(pdf_ok / total * 100, 1) if total > 0 else 0,
        },
        "enriquecimiento": {
            "total_facturas": total_prelim,
            "enriquecidas": enriquecidos,
            "clasificadas_ia": clasificados,
            "pct_enriquecimiento": round(enriquecidos / total_prelim * 100, 1) if total_prelim > 0 else 0,
            "pct_clasificacion": round(clasificados / total_prelim * 100, 1) if total_prelim > 0 else 0,
        },
    }


# ═══════════════════════════════════════════════════════════════════
# 6. TIPIFICACIONES QUANTA (Categorización empresarial)
# ═══════════════════════════════════════════════════════════════════

def get_tipificaciones(cliente_id: str, periodo: str) -> dict:
    """
    Business categorization breakdown based on AI classification.
    Groups expenses/income by `categoria` and `cuenta_contable`.
    """
    supabase = get_supabase()

    # Compras agrupadas por categoría
    res_c = supabase.table("sire_preliminar_compras") \
        .select("categoria, cuenta_contable, descripcion_cuenta, total_cp, bi_gravado_dg, igv_ipm_dg") \
        .eq("cliente_id", cliente_id) \
        .eq("periodo", periodo) \
        .not_.is_("categoria", "null") \
        .execute()

    # Ventas agrupadas por categoría
    res_v = supabase.table("sire_preliminar_ventas") \
        .select("categoria, cuenta_contable, descripcion_cuenta, total_cp, bi_gravada, igv_ipm") \
        .eq("cliente_id", cliente_id) \
        .eq("periodo", periodo) \
        .not_.is_("categoria", "null") \
        .execute()

    def _agrupar(records, campo_bi, campo_igv):
        grupos = {}
        for r in records:
            cat = r.get("categoria") or "Sin categoría"
            if cat not in grupos:
                grupos[cat] = {
                    "categoria": cat,
                    "cantidad": 0,
                    "total": 0.0,
                    "base_imponible": 0.0,
                    "igv": 0.0,
                    "cuentas": {},
                }
            grupos[cat]["cantidad"] += 1
            grupos[cat]["total"] += _safe_float(r.get("total_cp"))
            grupos[cat]["base_imponible"] += _safe_float(r.get(campo_bi))
            grupos[cat]["igv"] += _safe_float(r.get(campo_igv))

            cuenta = r.get("cuenta_contable") or "N/A"
            if cuenta not in grupos[cat]["cuentas"]:
                grupos[cat]["cuentas"][cuenta] = {
                    "codigo": cuenta,
                    "descripcion": r.get("descripcion_cuenta") or "",
                    "cantidad": 0,
                    "total": 0.0,
                }
            grupos[cat]["cuentas"][cuenta]["cantidad"] += 1
            grupos[cat]["cuentas"][cuenta]["total"] += _safe_float(r.get("total_cp"))

        # Convert cuentas dict to list and round values
        for g in grupos.values():
            g["total"] = round(g["total"], 2)
            g["base_imponible"] = round(g["base_imponible"], 2)
            g["igv"] = round(g["igv"], 2)
            g["cuentas"] = sorted(g["cuentas"].values(), key=lambda x: -x["total"])
            for c in g["cuentas"]:
                c["total"] = round(c["total"], 2)

        return sorted(grupos.values(), key=lambda x: -x["total"])

    return {
        "periodo": periodo,
        "compras_por_categoria": _agrupar(res_c.data or [], "bi_gravado_dg", "igv_ipm_dg"),
        "ventas_por_categoria": _agrupar(res_v.data or [], "bi_gravada", "igv_ipm"),
        "total_categorias_compras": len(set(r.get("categoria") for r in (res_c.data or []) if r.get("categoria"))),
        "total_categorias_ventas": len(set(r.get("categoria") for r in (res_v.data or []) if r.get("categoria"))),
    }


# ═══════════════════════════════════════════════════════════════════
# 7. LIBRO DIARIO (Vista Unificada)
# ═══════════════════════════════════════════════════════════════════

def get_libro_diario(
    cliente_id: str,
    periodo: str,
    page: int = 1,
    page_size: int = 100,
) -> dict:
    """
    Unified daily book combining purchases and sales, sorted by date.
    Includes accounting classification data.
    """
    supabase = get_supabase()

    # Get client info
    cli = supabase.table("clientes").select("ruc, razon_social").eq("id", cliente_id).execute()
    ruc_cliente = cli.data[0]["ruc"] if cli.data else ""

    # Get purchases
    res_c = supabase.table("sire_preliminar_compras") \
        .select("fecha_emision, serie_cdp, nro_cp, nro_doc_identidad, razon_social, "
                "bi_gravado_dg, igv_ipm_dg, total_cp, moneda, cuenta_contable, "
                "descripcion_cuenta, categoria, descripcion_comprobante") \
        .eq("cliente_id", cliente_id) \
        .eq("periodo", periodo) \
        .execute()

    # Get sales
    res_v = supabase.table("sire_preliminar_ventas") \
        .select("fecha_emision, serie_cdp, nro_cp, nro_doc_identidad, razon_social, "
                "bi_gravada, igv_ipm, total_cp, moneda, cuenta_contable, "
                "descripcion_cuenta, categoria, descripcion_comprobante") \
        .eq("cliente_id", cliente_id) \
        .eq("periodo", periodo) \
        .execute()

    # Unify
    entries = []
    for r in (res_c.data or []):
        entries.append({
            "libro": "COMPRAS",
            "fecha": r.get("fecha_emision"),
            "serie": r.get("serie_cdp"),
            "numero": r.get("nro_cp"),
            "ruc_tercero": r.get("nro_doc_identidad"),
            "razon_social": r.get("razon_social"),
            "base_imponible": _safe_float(r.get("bi_gravado_dg")),
            "igv": _safe_float(r.get("igv_ipm_dg")),
            "total": _safe_float(r.get("total_cp")),
            "moneda": r.get("moneda"),
            "cuenta_contable": r.get("cuenta_contable"),
            "descripcion_cuenta": r.get("descripcion_cuenta"),
            "categoria": r.get("categoria"),
            "glosa": r.get("descripcion_comprobante"),
        })

    for r in (res_v.data or []):
        entries.append({
            "libro": "VENTAS",
            "fecha": r.get("fecha_emision"),
            "serie": r.get("serie_cdp"),
            "numero": r.get("nro_cp"),
            "ruc_tercero": r.get("nno_doc_identidad"),
            "razon_social": r.get("razon_social"),
            "base_imponible": _safe_float(r.get("bi_gravada")),
            "igv": _safe_float(r.get("igv_ipm")),
            "total": _safe_float(r.get("total_cp")),
            "moneda": r.get("moneda"),
            "cuenta_contable": r.get("cuenta_contable"),
            "descripcion_cuenta": r.get("descripcion_cuenta"),
            "categoria": r.get("categoria"),
            "glosa": r.get("descripcion_comprobante"),
        })

    # Sort by date
    entries.sort(key=lambda x: x.get("fecha") or "")

    # Paginate
    total = len(entries)
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "data": entries[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
