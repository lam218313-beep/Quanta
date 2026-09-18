"""
Processing Maintenance Routes — Quanta

Resets and manual-correction endpoints for the SIRE preliminar / XML
enrichment / AI classification pipeline, plus manual comprobante file
management. Migrated from the legacy monolithic app/api.py.

Note: this is unrelated to app/brain/tasks/processing.py (the document OCR
pipeline) — same-ish name, different concern, kept as a separate module.
"""
import re
import sys
import threading
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from app.brain.db.supabase_client import get_supabase
from app.brain.routes.bot import _run_sync_process, ROOT_DIR

router = APIRouter(prefix="/api", tags=["processing"])


class ManualMatchRequest(BaseModel):
    ruc: str
    periodo: str
    tipo_libro: str


@router.post("/sire/manual-xml-match")
def manual_xml_match(req: ManualMatchRequest):
    script_path = ROOT_DIR / "app" / "brain" / "db" / "sire_xml_manual_enricher.py"
    cmd = [
        sys.executable,
        str(script_path),
        "--ruc", req.ruc,
        "--periodo", req.periodo,
        "--tipo", req.tipo_libro
    ]

    task_id = f"manual_match_{req.ruc}_{req.periodo}_{req.tipo_libro}"

    # Executar de forma asíncrona usando threading como los otros bots
    thread = threading.Thread(target=_run_sync_process, args=(task_id, cmd, str(ROOT_DIR)))
    thread.daemon = True
    thread.start()

    return {"message": "Iniciado el acoplamiento manual de XMLs.", "task_id": task_id}


# ─────────────────────────────────────────────
# RESETEAR ENRIQUECIMIENTO XML
# ─────────────────────────────────────────────

class ResetEnriquecimientoRequest(BaseModel):
    ruc: str
    periodo: str
    tipo_libro: str | None = None  # "VENTAS", "COMPRAS", o None = ambos


@router.post("/enriquecimiento-xml/reset")
def reset_enriquecimiento_xml(req: ResetEnriquecimientoRequest):
    """Borra el enriquecimiento XML (estado_enriquecimiento, descripcion_comprobante, detraccion)
    de todos los comprobantes del cliente+periodo indicados,
    para poder volver a extraer la información de los XML desde cero.
    """
    supabase = get_supabase()

    # Resolver cliente_id
    res_cli = supabase.table("clientes").select("id").eq("ruc", req.ruc).execute()
    if not res_cli.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente_id = res_cli.data[0]["id"]

    campos_reset = {
        "estado_enriquecimiento": None,
        "descripcion_comprobante": None,
        "detraccion": None,
    }

    totales = {"VENTAS": 0, "COMPRAS": 0}
    tablas = []

    tipo = (req.tipo_libro or "").upper()
    if tipo == "VENTAS":
        tablas = [("sire_preliminar_ventas", "VENTAS")]
    elif tipo == "COMPRAS":
        tablas = [("sire_preliminar_compras", "COMPRAS")]
    else:
        tablas = [
            ("sire_preliminar_ventas", "VENTAS"),
            ("sire_preliminar_compras", "COMPRAS"),
        ]

    for tabla, label in tablas:
        # Solo resetear los que ya tenían estado de enriquecimiento (evitar tocar los que nunca se enriquecieron)
        res = supabase.table(tabla) \
            .update(campos_reset) \
            .eq("cliente_id", cliente_id) \
            .eq("periodo", req.periodo) \
            .not_.is_("estado_enriquecimiento", "null") \
            .execute()
        count = len(res.data) if res.data else 0
        totales[label] = count
        print(f"[reset-xml] {label}: {count} registros limpiados (cliente {req.ruc}, periodo {req.periodo})")

    return {
        "ok": True,
        "ruc": req.ruc,
        "periodo": req.periodo,
        "limpiados": totales,
        "mensaje": f"Enriquecimiento XML eliminado: {totales['VENTAS']} ventas y {totales['COMPRAS']} compras."
    }


# ─────────────────────────────────────────────
# RESETEAR CLASIFICACIÓN IA
# ─────────────────────────────────────────────

class ResetClasificacionRequest(BaseModel):
    ruc: str
    periodo: str
    tipo_libro: str | None = None  # "VENTAS", "COMPRAS", o None = ambos


@router.post("/clasificacion-ia/reset")
def reset_clasificacion_ia(req: ResetClasificacionRequest):
    """Borra la clasificación IA (cuenta_contable, descripcion_cuenta, categoria)
    de todos los comprobantes del cliente+periodo indicados,
    para poder volver a correr el clasificador desde cero.
    """
    supabase = get_supabase()

    # Resolver cliente_id
    res_cli = supabase.table("clientes").select("id").eq("ruc", req.ruc).execute()
    if not res_cli.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente_id = res_cli.data[0]["id"]

    campos_reset = {
        "cuenta_contable": None,
        "descripcion_cuenta": None,
        "categoria": None,
    }

    totales = {"VENTAS": 0, "COMPRAS": 0}
    tablas = []

    tipo = (req.tipo_libro or "").upper()
    if tipo == "VENTAS":
        tablas = [("sire_preliminar_ventas", "VENTAS")]
    elif tipo == "COMPRAS":
        tablas = [("sire_preliminar_compras", "COMPRAS")]
    else:
        tablas = [
            ("sire_preliminar_ventas", "VENTAS"),
            ("sire_preliminar_compras", "COMPRAS"),
        ]

    for tabla, label in tablas:
        # Solo resetear los que ya tenían cuenta asignada (evitar tocar los que nunca se clasificaron)
        res = supabase.table(tabla) \
            .update(campos_reset) \
            .eq("cliente_id", cliente_id) \
            .eq("periodo", req.periodo) \
            .not_.is_("cuenta_contable", "null") \
            .execute()
        count = len(res.data) if res.data else 0
        totales[label] = count
        print(f"[reset-ia] {label}: {count} registros limpiados (cliente {req.ruc}, periodo {req.periodo})")

    return {
        "ok": True,
        "ruc": req.ruc,
        "periodo": req.periodo,
        "limpiados": totales,
        "mensaje": f"Clasificación IA eliminada: {totales['VENTAS']} ventas y {totales['COMPRAS']} compras."
    }


# ─────────────────────────────────────────────
# RESETEAR PRELIMINAR SIRE
# ─────────────────────────────────────────────

@router.post("/preliminar/reset")
def reset_preliminar_sire(req: ResetClasificacionRequest):
    """Borra la data preliminar del SIRE y los registros físicos asociados
    del cliente+periodo indicados, para poder volver a subirlos/cargarlos.
    """
    supabase = get_supabase()

    # Resolver cliente_id
    res_cli = supabase.table("clientes").select("id").eq("ruc", req.ruc).execute()
    if not res_cli.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente_id = res_cli.data[0]["id"]

    tipo = (req.tipo_libro or "").upper()

    # 1. Primero borrar de sire_comprobantes_fisicos por dependencias
    query_fisicos = supabase.table("sire_comprobantes_fisicos").delete().eq("cliente_id", cliente_id).eq("periodo", req.periodo)
    if tipo in ("VENTAS", "COMPRAS"):
        query_fisicos = query_fisicos.eq("tipo_libro", tipo)
    query_fisicos.execute()

    totales = {"VENTAS": 0, "COMPRAS": 0}
    tablas = []

    if tipo == "VENTAS":
        tablas = [("sire_preliminar_ventas", "VENTAS")]
    elif tipo == "COMPRAS":
        tablas = [("sire_preliminar_compras", "COMPRAS")]
    else:
        tablas = [
            ("sire_preliminar_ventas", "VENTAS"),
            ("sire_preliminar_compras", "COMPRAS"),
        ]

    for tabla, label in tablas:
        res = supabase.table(tabla) \
            .delete() \
            .eq("cliente_id", cliente_id) \
            .eq("periodo", req.periodo) \
            .execute()
        count = len(res.data) if res.data else 0
        totales[label] = count
        print(f"[reset-preliminar] {label}: {count} registros eliminados (cliente {req.ruc}, periodo {req.periodo})")

    return {
        "ok": True,
        "ruc": req.ruc,
        "periodo": req.periodo,
        "limpiados": totales,
        "mensaje": f"Preliminar SIRE eliminado: {totales['VENTAS']} ventas y {totales['COMPRAS']} compras."
    }


# ─────────────────────────────────────────────
# GESTIÓN MANUAL DE COMPROBANTES FÍSICOS
# ─────────────────────────────────────────────

ESTADOS_VALIDOS = {"PENDIENTE", "DESCARGADO", "ERROR", "NO_EXISTE", "NO_DESCARGABLE", "DESFASADO"}


class UpdateEstadoRequest(BaseModel):
    estado_xml: str | None = None
    estado_pdf: str | None = None
    reset_reintentos: bool = True


@router.patch("/comprobante/{comprobante_id}/estado")
def update_comprobante_estado(comprobante_id: str, req: UpdateEstadoRequest):
    """Actualiza manualmente el estado XML y/o PDF de un comprobante físico.
    Permite por ejemplo pasar de NO_EXISTE a PENDIENTE para forzar un reintento.
    """
    supabase = get_supabase()

    # Validaciones
    if req.estado_xml and req.estado_xml not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=400, detail=f"estado_xml inválido. Valores permitidos: {ESTADOS_VALIDOS}")
    if req.estado_pdf and req.estado_pdf not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=400, detail=f"estado_pdf inválido. Valores permitidos: {ESTADOS_VALIDOS}")
    if not req.estado_xml and not req.estado_pdf:
        raise HTTPException(status_code=400, detail="Debe indicar al menos estado_xml o estado_pdf")

    # Verificar que el comprobante existe
    check = supabase.table("sire_comprobantes_fisicos").select("*").eq("id", comprobante_id).execute()
    if not check.data:
        raise HTTPException(status_code=404, detail="Comprobante no encontrado")

    comp = check.data[0]
    update_data = {}
    if req.estado_xml:
        update_data["estado_xml"] = req.estado_xml
    if req.estado_pdf:
        update_data["estado_pdf"] = req.estado_pdf
    if req.reset_reintentos:
        update_data["reintentos"] = 0
        update_data["error_log"] = None

    # Eliminar archivo físico SOLO si cambiamos el estado a PENDIENTE o ERROR.
    # NO borrar si el estado es DESCARGADO, NO_DESCARGABLE, NO_EXISTE o DESFASADO.
    ESTADOS_SIN_BORRADO = {"DESCARGADO", "NO_DESCARGABLE", "NO_EXISTE", "DESFASADO"}

    base_name = f"{comp.get('ruc_tercero', '')}-{comp.get('tipo_cp', '')}-{comp.get('serie', '')}-{comp.get('numero', '')}"
    downloads_dir = ROOT_DIR / "downloads"

    if downloads_dir.exists():
        if req.estado_xml and req.estado_xml not in ESTADOS_SIN_BORRADO:
            for f in downloads_dir.rglob(f"{base_name}.*"):
                if f.suffix.lower() in ('.xml', '.zip'):
                    try:
                        f.unlink()
                    except Exception:
                        pass
        if req.estado_pdf and req.estado_pdf not in ESTADOS_SIN_BORRADO:
            for f in downloads_dir.rglob(f"{base_name}.*"):
                if f.suffix.lower() == '.pdf':
                    try:
                        f.unlink()
                    except Exception:
                        pass

    supabase.table("sire_comprobantes_fisicos").update(update_data).eq("id", comprobante_id).execute()
    return {"ok": True, "id": comprobante_id, "updated": update_data}


# ─────────────────────────────────────────────
# RESET MASIVO A PENDIENTE (excluyendo DESCARGADO)
# ─────────────────────────────────────────────

class ResetPendientesRequest(BaseModel):
    ruc: str
    periodo: str | None = None
    tipo_libro: str | None = None   # "VENTAS", "COMPRAS" o None = ambos


@router.post("/comprobantes/reset-pendientes")
def reset_comprobantes_pendientes(req: ResetPendientesRequest):
    """Pone en PENDIENTE todos los comprobantes físicos cuyo estado_xml o estado_pdf
    NO sea DESCARGADO. Excluye los comprobantes ya descargados.
    Útil para forzar un nuevo intento masivo del bot descargador.
    """
    supabase = get_supabase()

    # Resolver cliente_id
    res_cli = supabase.table("clientes").select("id").eq("ruc", req.ruc).execute()
    if not res_cli.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente_id = res_cli.data[0]["id"]

    # Construir la query base para estados != DESCARGADO y != DESFASADO
    # Para XML: resetear si NO está DESCARGADO ni DESFASADO
    # Para PDF: resetear si NO está DESCARGADO ni DESFASADO
    query_xml = (
        supabase.table("sire_comprobantes_fisicos")
        .update({"estado_xml": "PENDIENTE", "reintentos": 0, "error_log": None})
        .eq("cliente_id", cliente_id)
        .neq("estado_xml", "DESCARGADO")
        .neq("estado_xml", "DESFASADO")
    )
    query_pdf = (
        supabase.table("sire_comprobantes_fisicos")
        .update({"estado_pdf": "PENDIENTE", "reintentos": 0, "error_log": None})
        .eq("cliente_id", cliente_id)
        .neq("estado_pdf", "DESCARGADO")
        .neq("estado_pdf", "DESFASADO")
    )

    if req.periodo:
        query_xml = query_xml.eq("periodo", req.periodo)
        query_pdf = query_pdf.eq("periodo", req.periodo)

    if req.tipo_libro:
        query_xml = query_xml.eq("tipo_libro", req.tipo_libro.upper())
        query_pdf = query_pdf.eq("tipo_libro", req.tipo_libro.upper())

    res_xml = query_xml.execute()
    res_pdf = query_pdf.execute()

    total_xml = len(res_xml.data) if res_xml.data else 0
    total_pdf = len(res_pdf.data) if res_pdf.data else 0

    print(f"[reset-pendientes] {req.ruc} | periodo={req.periodo} | tipo={req.tipo_libro}")
    print(f"  → XML reseteados: {total_xml} | PDF reseteados: {total_pdf}")

    return {
        "ok": True,
        "ruc": req.ruc,
        "periodo": req.periodo,
        "tipo_libro": req.tipo_libro,
        "reseteados_xml": total_xml,
        "reseteados_pdf": total_pdf,
        "mensaje": f"Se pusieron en PENDIENTE {total_xml} XML y {total_pdf} PDF (excluyendo DESCARGADO)."
    }


@router.post("/comprobante/{comprobante_id}/upload")
async def upload_comprobante_file(
    comprobante_id: str,
    file: UploadFile = File(...),
    file_type: str = Form(...),  # "pdf" o "xml"
):
    """Sube manualmente un archivo PDF o XML para un comprobante físico.
    Guarda el archivo en la carpeta de downloads del cliente y actualiza la ruta en DB.
    """
    supabase = get_supabase()

    # Verificar que el comprobante existe y obtener sus datos
    check = supabase.table("sire_comprobantes_fisicos") \
        .select("id, cliente_id, periodo, tipo_libro, serie, numero, tipo_cp, ruc_tercero, clientes!inner(ruc, razon_social)") \
        .eq("id", comprobante_id) \
        .execute()

    if not check.data:
        raise HTTPException(status_code=404, detail="Comprobante no encontrado")

    comp = check.data[0]
    cliente = comp.get("clientes", {})
    ruc_cliente = cliente.get("ruc", "unknown")
    rs_cliente = (cliente.get("razon_social") or "").strip().replace("/", "-").replace("\\", "-")

    # Sanitizar nombre de carpeta (igual que en el scraper)
    rs_safe = re.sub(r'[\\/*?"<>|]', "", rs_cliente).strip()
    folder_client = f"{rs_safe} {ruc_cliente}".strip()

    # Validar tipo
    file_type = file_type.lower()
    if file_type not in ("pdf", "xml"):
        raise HTTPException(status_code=400, detail="file_type debe ser 'pdf' o 'xml'")

    # Determinar extensión real
    original_name = file.filename or ""
    ext = Path(original_name).suffix.lower() or f".{file_type}"
    if ext not in (".pdf", ".xml", ".zip"):
        ext = f".{file_type}"

    # Construir ruta destino (misma estructura que el scraper)
    period = comp.get("periodo", "unknown")
    book = "sales" if comp.get("tipo_libro") == "VENTAS" else "purchases"
    subfolder = "pdf" if file_type == "pdf" else "xml"

    ruc_tercero = (comp.get("ruc_tercero") or "").strip()
    if ruc_tercero == "-":
        ruc_tercero = ""
    ruc_tercero = ruc_tercero or ruc_cliente

    tipo_cp = comp.get("tipo_cp", "00")
    serie = comp.get("serie", "")
    numero = comp.get("numero", "")
    base_name = f"{ruc_tercero}-{tipo_cp}-{serie}-{numero}"

    dest_dir = ROOT_DIR / "downloads" / "xml" / folder_client / period / book / subfolder
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / f"{base_name}{ext}"

    # Escribir el archivo
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="El archivo está vacío")

    with open(dest_path, "wb") as f:
        f.write(contents)

    # Actualizar DB
    update_data: dict = {}
    if file_type == "pdf":
        update_data["ruta_pdf"] = str(dest_path)
        update_data["estado_pdf"] = "DESCARGADO"
    else:
        update_data["ruta_xml"] = str(dest_path)
        update_data["estado_xml"] = "DESCARGADO"
    update_data["reintentos"] = 0
    update_data["error_log"] = None

    supabase.table("sire_comprobantes_fisicos").update(update_data).eq("id", comprobante_id).execute()

    return {
        "ok": True,
        "id": comprobante_id,
        "file_type": file_type,
        "saved_to": str(dest_path),
        "size_bytes": len(contents),
    }
