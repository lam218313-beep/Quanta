from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
from datetime import datetime
from typing import Optional
import fitz  # PyMuPDF

from app.brain.pdf_generator import generate_invoice_pdf_from_xml, generate_client_report_pdf, generate_financial_report_pdf
from app.brain.db.supabase_client import get_supabase

router = APIRouter(prefix="/api/pdf", tags=["pdf"])

TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads", "tmp_pdf")
os.makedirs(TEMP_DIR, exist_ok=True)

TIPO_CP_LABELS = {
    "01": "Factura", "03": "Boleta", "07": "N. Crédito", "08": "N. Débito",
    "09": "Guía Remisión", "20": "Retención", "40": "Percepción",
}
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
          "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

ESTADO_CLASS = {"ERROR": "error", "PARCIAL": "parcial", "COMPLETO": "completo"}
ESTADO_LABEL = {"ERROR": "Error", "PARCIAL": "Parcial", "COMPLETO": "Completo", "PENDIENTE": "Pendiente"}


def _tipo_cp_label(code):
    if not code:
        return "Sin tipo"
    return TIPO_CP_LABELS.get(code, f"Tipo {code}")


def _fmt_currency(value: float) -> str:
    return f"S/ {value:,.2f}"


def _periodo_label(periodo: str) -> str:
    if not periodo or len(periodo) != 6:
        return periodo or ""
    year, month = periodo[:4], periodo[4:6]
    try:
        return f"{MESES[int(month) - 1]} {year}"
    except (ValueError, IndexError):
        return periodo


@router.post("/invoice")
async def generate_invoice_pdf(file: UploadFile = File(...)):
    """Generate a PDF from an uploaded SUNAT XML file."""
    if file.content_type not in ["text/xml", "application/xml"]:
        raise HTTPException(400, "File must be an XML")

    xml_content = await file.read()
    output_filename = f"invoice_{uuid.uuid4().hex}.pdf"
    output_path = os.path.join(TEMP_DIR, output_filename)

    try:
        await generate_invoice_pdf_from_xml(xml_content, output_path)
        return FileResponse(path=output_path, filename="factura.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(500, f"Error generating PDF: {str(e)}")


class ReportRequest(BaseModel):
    cliente_id: str
    periodo: str


@router.post("/report")
async def generate_report_pdf(req: ReportRequest):
    """
    Generate the full financial report PDF for a client + period — same
    data source and calculations as the Dashboard page (v_libro_unificado),
    so the PDF always matches what's on screen.
    """
    supabase = get_supabase()

    c_res = supabase.table("clientes").select("*").eq("id", req.cliente_id).execute()
    if not c_res.data:
        raise HTTPException(404, "Cliente no encontrado")
    cliente = c_res.data[0]

    doc_res = supabase.table("v_libro_unificado") \
        .select("*") \
        .eq("ruc", cliente["ruc"]) \
        .eq("periodo", req.periodo) \
        .order("fecha_emision", desc=True) \
        .execute()
    documentos = doc_res.data or []

    ventas = [d for d in documentos if d.get("libro") != "COMPRAS"]
    compras = [d for d in documentos if d.get("libro") == "COMPRAS"]

    total_ventas = sum(float(d.get("total_cp") or 0) for d in ventas)
    total_compras = sum(float(d.get("total_cp") or 0) for d in compras)
    igv_ventas = sum(float(d.get("igv") or 0) for d in ventas)
    igv_compras = sum(float(d.get("igv") or 0) for d in compras)
    igv_pagar = igv_ventas - igv_compras

    procesados_completos = sum(1 for d in documentos if d.get("estado_enriquecimiento") == "COMPLETO")
    total_docs = len(documentos)
    tasa_procesamiento = round((procesados_completos / total_docs) * 100) if total_docs > 0 else 0

    kpis = {
        "total_ventas_fmt": _fmt_currency(total_ventas),
        "total_compras_fmt": _fmt_currency(total_compras),
        "igv_fmt": _fmt_currency(abs(igv_pagar)),
        "igv_a_pagar": igv_pagar > 0,
        "tasa_procesamiento": tasa_procesamiento,
        "procesados_completos": procesados_completos,
        "total_docs": total_docs,
        "docs_ventas": len(ventas),
        "docs_compras": len(compras),
    }

    # Distribución de compras por tipo de comprobante
    tipo_map = {}
    for d in compras:
        label = _tipo_cp_label(d.get("tipo_cp_doc"))
        tipo_map[label] = tipo_map.get(label, 0) + float(d.get("total_cp") or 0)
    distribucion = []
    for label, monto in sorted(tipo_map.items(), key=lambda x: -x[1]):
        pct = round((monto / total_compras) * 100) if total_compras > 0 else 0
        distribucion.append({"label": label, "monto_fmt": _fmt_currency(monto), "pct": pct})

    # Balance del periodo
    utilidad = total_ventas - total_compras
    max_balance = max(total_ventas, total_compras, abs(utilidad), 1)
    balance = [
        {"label": "Ventas", "monto_fmt": _fmt_currency(total_ventas), "pct": min(100, round((total_ventas / max_balance) * 100)), "color": "#10b981"},
        {"label": "Compras", "monto_fmt": _fmt_currency(total_compras), "pct": min(100, round((total_compras / max_balance) * 100)), "color": "#ef4444"},
        {"label": "Utilidad Bruta", "monto_fmt": _fmt_currency(utilidad), "pct": min(100, round((abs(utilidad) / max_balance) * 100)), "color": "#3b82f6" if utilidad >= 0 else "#f59e0b"},
    ]

    # Top 5 clientes / proveedores
    def _top_entidades(docs):
        m = {}
        for d in docs:
            nombre = d.get("nombre_tercero") or "Desconocido"
            m[nombre] = m.get(nombre, 0) + float(d.get("total_cp") or 0)
        top = sorted(m.items(), key=lambda x: -x[1])[:5]
        return [{"nombre": n, "monto_fmt": _fmt_currency(v)} for n, v in top]

    top_clientes = _top_entidades(ventas)
    top_proveedores = _top_entidades(compras)

    # Últimos movimientos (ya vienen ordenados desc por fecha_emision)
    movimientos = [{
        "fecha": d.get("fecha_emision") or "-",
        "es_venta": d.get("libro") != "COMPRAS",
        "entidad": d.get("nombre_tercero") or "-",
        "monto_fmt": _fmt_currency(float(d.get("total_cp") or 0)),
    } for d in documentos[:25]]

    # Documentos observados
    observados = []
    for d in documentos:
        estado = d.get("estado_enriquecimiento")
        if estado == "COMPLETO":
            continue
        observados.append({
            "comprobante": f"{_tipo_cp_label(d.get('tipo_cp_doc'))}-{d.get('serie_cdp', '')}-{d.get('nro_cp', '')}",
            "entidad": d.get("nombre_tercero") or "-",
            "estado_class": ESTADO_CLASS.get(estado, "pendiente"),
            "estado_label": ESTADO_LABEL.get(estado, "Pendiente"),
        })

    report_data = {
        "cliente": {"ruc": cliente.get("ruc", ""), "razon_social": cliente.get("razon_social", "")},
        "periodo_label": _periodo_label(req.periodo),
        "fecha_generacion": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "kpis": kpis,
        "distribucion": distribucion,
        "balance": balance,
        "top_clientes": top_clientes,
        "top_proveedores": top_proveedores,
        "movimientos": movimientos,
        "observados": observados[:50],
    }

    output_filename = f"report_{req.cliente_id}_{req.periodo}.pdf"
    output_path = os.path.join(TEMP_DIR, output_filename)

    try:
        await generate_financial_report_pdf(report_data, output_path)
    except Exception as e:
        raise HTTPException(500, f"Error generando el informe: {str(e)}")

    _merge_attachments(supabase, output_path, req.cliente_id, req.periodo)

    return FileResponse(path=output_path, filename=f"Informe_{req.periodo}.pdf", media_type="application/pdf")


def _merge_attachments(supabase, report_path: str, cliente_id: str, periodo: str) -> None:
    """
    Appends every client_attachments PDF for this cliente+periodo onto the
    end of the report at report_path, in upload order. Never raises — a
    bad attachment is skipped and logged, the base report is always served.
    """
    STORAGE_BUCKET = "client-attachments"

    try:
        res = (
            supabase.table("client_attachments")
            .select("storage_path")
            .eq("cliente_id", cliente_id)
            .eq("periodo", periodo)
            .order("created_at")
            .execute()
        )
        attachments = res.data or []
    except Exception as e:
        print(f"[attachments] No se pudo consultar client_attachments: {e}")
        return

    if not attachments:
        return

    report_doc = fitz.open(report_path)
    merged_any = False

    for att in attachments:
        try:
            content = supabase.storage.from_(STORAGE_BUCKET).download(att["storage_path"])
            attachment_doc = fitz.open(stream=content, filetype="pdf")
            report_doc.insert_pdf(attachment_doc)
            attachment_doc.close()
            merged_any = True
        except Exception as e:
            print(f"[attachments] No se pudo fusionar {att['storage_path']}: {e}")
            continue

    if merged_any:
        report_doc.saveIncr() if report_doc.can_save_incrementally() else report_doc.save(report_path, incremental=False)
    report_doc.close()
