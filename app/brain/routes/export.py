"""
Export Routes — Quanta

PDF merging, SIRE TXT generation, and Excel exports (preliminar + enriquecido)
for a client's period. Migrated from the legacy monolithic app/api.py.
"""
import os
import io
import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse, PlainTextResponse
from pydantic import BaseModel

from app.brain.db.supabase_client import get_supabase
from app.brain.utils.pagination import fetch_all_records

router = APIRouter(prefix="/api/export", tags=["export"])


class ExportPdfRequest(BaseModel):
    ruc: str
    periodo: str
    tipo_libro: str
    allow_incomplete: bool = False


class ExportPreliminarRequest(BaseModel):
    ruc: str
    periodo: str


class ExportSireTxtRequest(BaseModel):
    ruc: str
    periodo: str
    tipo_libro: str


def _safe_remove_file(path: str) -> None:
    try:
        os.remove(path)
    except Exception:
        # Best-effort cleanup; avoid surfacing Windows file-lock errors.
        pass


@router.post("/pdf-merged")
def export_pdf_merged(req: ExportPdfRequest, background_tasks: BackgroundTasks):
    supabase = get_supabase()

    # Obtener el id del cliente
    res_cli = supabase.table("clientes").select("id").eq("ruc", req.ruc).execute()
    if not res_cli.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente_id = res_cli.data[0]["id"]

    # Obtener las rutas de los pdf y datos del comprobante de ese cliente, periodo y tipo
    res_docs = fetch_all_records("sire_comprobantes_fisicos", supabase, "id, serie, numero, ruta_pdf", {"cliente_id": cliente_id, "periodo": req.periodo, "tipo_libro": req.tipo_libro})

    if not res_docs.data:
        raise HTTPException(status_code=404, detail="No hay comprobantes para exportar")

    comprobantes = res_docs.data
    failed_comprobantes = []

    try:
        merged_doc = fitz.open()
        for comp in comprobantes:
            pdf_path = comp.get("ruta_pdf")
            serie = comp.get("serie", "N/A")
            numero = comp.get("numero", "N/A")

            if not pdf_path or not os.path.exists(pdf_path):
                failed_comprobantes.append(comp)
                continue

            try:
                doc = fitz.open(pdf_path)
                merged_doc.insert_pdf(doc)
                doc.close()
            except Exception as e:
                print(f"Error merging {pdf_path}: {e}")
                failed_comprobantes.append(comp)

        # Si todos fallaron, no hay nada que compilar
        if len(failed_comprobantes) == len(comprobantes):
            merged_doc.close()
            raise HTTPException(status_code=400, detail="Ningún comprobante tiene un PDF válido o descargado para compilar.")

        # Si hubo comprobantes que fallaron y NO se permite incompleto, abortar
        if failed_comprobantes and not req.allow_incomplete:
            merged_doc.close()
            failed_names = []

            for fcomp in failed_comprobantes:
                failed_names.append(f"{fcomp.get('serie')}-{fcomp.get('numero')}")
                # Actualizar a PENDIENTE para que el bot vuelva a intentarlo
                supabase.table("sire_comprobantes_fisicos").update({
                    "estado_xml": "PENDIENTE",
                    "estado_pdf": "PENDIENTE",
                    "reintentos": 0
                }).eq("id", fcomp["id"]).execute()

            error_msg = f"No se pudo generar el compilado PDF porque los siguientes comprobantes no se descargaron correctamente o están corruptos: {', '.join(failed_names)}. Se han devuelto a estado PENDIENTE."
            raise HTTPException(status_code=400, detail=error_msg)

        # Si se permite incompleto, solo marcar los fallidos como PENDIENTE sin abortar
        if failed_comprobantes and req.allow_incomplete:
            for fcomp in failed_comprobantes:
                supabase.table("sire_comprobantes_fisicos").update({
                    "estado_pdf": "PENDIENTE",
                    "reintentos": 0
                }).eq("id", fcomp["id"]).execute()

        # Guardar en un archivo temporal si todo está correcto
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.close()
        merged_doc.save(tmp.name)
        merged_doc.close()

        filename = f"Comprobantes_{req.tipo_libro}_{req.periodo}.pdf"
        background_tasks.add_task(_safe_remove_file, tmp.name)
        return FileResponse(tmp.name, filename=filename, media_type="application/pdf")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sire-txt")
def export_sire_txt(req: ExportSireTxtRequest):
    """Genera el TXT personalizado para el sistema contable (M1)"""
    from app.brain.db.sire_txt_exporter import build_custom_compras_txt, build_custom_ventas_txt
    supabase = get_supabase()

    res_cli = supabase.table("clientes").select("id").eq("ruc", req.ruc).execute()
    if not res_cli.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente_id = res_cli.data[0]["id"]

    if req.tipo_libro == "COMPRAS":
        res = fetch_all_records("sire_preliminar_compras", supabase, "*", {"cliente_id": cliente_id, "periodo": req.periodo}, "fecha_emision")
        txt_content = build_custom_compras_txt(res.data, req.ruc, req.periodo)
        filename = f"Compras_{req.periodo}_M1.txt"
    else:
        res = fetch_all_records("sire_preliminar_ventas", supabase, "*", {"cliente_id": cliente_id, "periodo": req.periodo}, "fecha_emision")
        txt_content = build_custom_ventas_txt(res.data, req.ruc, req.periodo)
        filename = f"Ventas_{req.periodo}_M1.txt"

    return PlainTextResponse(content=txt_content, media_type="text/plain", headers={"Content-Disposition": f"attachment; filename={filename}"})


@router.post("/preliminar-excel")
def export_preliminar_excel(req: ExportPreliminarRequest):
    """Genera un Excel con 2 hojas (VENTAS, COMPRAS) con los datos crudos del
    Preliminar SIRE. La hoja VENTAS incluye al final un cuadro de
    Liquidación de Impuestos (RENTA MYPE 1%, IGV 18%, Crédito Fiscal, etc.)
    """
    supabase = get_supabase()

    # ── Resolver cliente ────────────────────────────────────────────────────
    res_cli = supabase.table("clientes").select("id, razon_social").eq("ruc", req.ruc).execute()
    if not res_cli.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente_id = res_cli.data[0]["id"]
    razon_social = res_cli.data[0]["razon_social"]

    periodo_fmt = req.periodo  # ej: "202605"
    try:
        yr, mo = int(periodo_fmt[:4]), int(periodo_fmt[4:])
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        periodo_label = f"{meses[mo-1]} {yr}"
    except Exception:
        periodo_label = periodo_fmt

    # ── Obtener datos ───────────────────────────────────────────────────────
    res_v = fetch_all_records("sire_preliminar_ventas", supabase, "*", {"cliente_id": cliente_id, "periodo": req.periodo}, "fecha_emision")

    res_c = fetch_all_records("sire_preliminar_compras", supabase, "*", {"cliente_id": cliente_id, "periodo": req.periodo}, "fecha_emision")

    ventas  = res_v.data or []
    compras = res_c.data or []

    # ── Estilos de utilidad ─────────────────────────────────────────────────
    def _fill(hex_color: str) -> PatternFill:
        return PatternFill("solid", fgColor=hex_color)

    def _border_all():
        s = Side(style="thin", color="AAAAAA")
        return Border(left=s, right=s, top=s, bottom=s)

    def _bold_font(size=10, color="000000"):
        return Font(bold=True, size=size, color=color)

    HEADER_FILL  = _fill("1A3C5E")   # azul oscuro
    HEADER_FONT  = Font(bold=True, color="FFFFFF", size=9)
    ALT_ROW_FILL = _fill("EBF3FA")   # azul muy claro para filas pares

    # Colores del cuadro liquidación (tomados de la imagen)
    DARK_NAVY   = _fill("1A3C5E")
    LIGHT_GRAY  = _fill("D9D9D9")
    YELLOW_FILL = _fill("FFFF00")
    RED_FONT    = Font(bold=True, color="FF0000", size=10)
    WHITE_FONT  = Font(bold=True, color="FFFFFF", size=10)
    NORMAL_FONT = Font(size=10)
    BOLD_FONT   = Font(bold=True, size=10)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "PRELIMINAR_SIRE"

    # ════════════════════════════════════════════════════════════════════════
    # HEADER DATOS CLIENTE
    # ════════════════════════════════════════════════════════════════════════
    ws.merge_cells("A1:K1")
    cell_title = ws.cell(row=1, column=1, value="CIERRE TRIBUTARIO MENSUAL")
    cell_title.font = _bold_font(size=14)
    cell_title.alignment = Alignment(horizontal="center", vertical="center")

    ws.merge_cells("A3:E3")
    ws.cell(row=3, column=1, value=f"Razón Social: {razon_social}").font = _bold_font(size=11)
    ws.merge_cells("A4:E4")
    ws.cell(row=4, column=1, value=f"RUC: {req.ruc}").font = _bold_font(size=11)
    ws.merge_cells("A5:E5")
    ws.cell(row=5, column=1, value=f"Periodo: {periodo_label}").font = _bold_font(size=11)

    r = 7
    header_v_row = r

    # ════════════════════════════════════════════════════════════════════════
    # TABLA VENTAS
    # ════════════════════════════════════════════════════════════════════════
    headers_v = [
        "Fecha Emisión", "Serie", "Número",
        "RUC / DNI", "Razón Social",
        "Base Imponible", "IGV / IPM", "Exonerado", "Inafecto",
        "TOTAL", "Moneda"
    ]
    for c, h in enumerate(headers_v, 1):
        cell = ws.cell(row=r, column=c, value=h)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = _border_all()
    ws.row_dimensions[r].height = 28

    total_bi_v = 0.0
    total_igv_v = 0.0
    total_cp_v  = 0.0

    for i, row in enumerate(ventas, 1):
        r += 1
        fill = ALT_ROW_FILL if i % 2 == 0 else None
        vals = [
            row.get("fecha_emision") or "",
            row.get("serie_cdp") or "",
            row.get("nro_cp") or "",
            row.get("nro_doc_identidad") or "",
            row.get("razon_social") or "",
            float(row.get("bi_gravada") or 0),
            float(row.get("igv_ipm") or 0),
            float(row.get("mto_exonerado") or 0),
            float(row.get("mto_inafecto") or 0),
            float(row.get("total_cp") or 0),
            row.get("moneda") or "PEN",
        ]
        total_bi_v  += vals[5]
        total_igv_v += vals[6]
        total_cp_v  += vals[9]

        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.border = _border_all()
            if fill:
                cell.fill = fill
            cell.alignment = Alignment(vertical="center")
            if c in (6, 7, 8, 9, 10):
                cell.number_format = '"S/"#,##0.00'

    # Fila de totales ventas
    total_row_v = r + 1
    r = total_row_v
    ws.cell(row=r, column=5, value="TOTAL VENTAS").font = _bold_font()
    ws.cell(row=r, column=5).fill = _fill("D9EDF7")
    for c, val in [(6, total_bi_v), (7, total_igv_v), (10, total_cp_v)]:
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = _bold_font()
        cell.fill = _fill("D9EDF7")
        cell.number_format = '"S/"#,##0.00'
        cell.border = _border_all()

    # ════════════════════════════════════════════════════════════════════════
    # TABLA COMPRAS
    # ════════════════════════════════════════════════════════════════════════
    r += 3
    r_compras_hdr = r

    headers_c = [
        "Fecha Emisión", "Serie", "Número",
        "RUC / DNI", "Razón Social",
        "BI Gravado", "IGV / IPM", "BI No Gravado", "Valor No Grav.",
        "TOTAL", "Moneda"
    ]
    for c, h in enumerate(headers_c, 1):
        cell = ws.cell(row=r, column=c, value=h)
        cell.fill = _fill("217346")
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = _border_all()
    ws.row_dimensions[r].height = 28

    total_bi_c = 0.0
    total_igv_c = 0.0
    total_cp_c2 = 0.0

    for i, row in enumerate(compras, 1):
        r += 1
        fill = ALT_ROW_FILL if i % 2 == 0 else None
        vals = [
            row.get("fecha_emision") or "",
            row.get("serie_cdp") or "",
            row.get("nro_cp") or "",
            row.get("nro_doc_identidad") or "",
            row.get("razon_social") or "",
            float(row.get("bi_gravado_dg") or 0),
            float(row.get("igv_ipm_dg") or 0),
            float(row.get("bi_gravado_dng") or 0),
            float(row.get("valor_adq_ng") or 0),
            float(row.get("total_cp") or 0),
            row.get("moneda") or "PEN",
        ]
        total_bi_c  += vals[5]
        total_igv_c += vals[6]
        total_cp_c2 += vals[9]

        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.border = _border_all()
            if fill:
                cell.fill = fill
            cell.alignment = Alignment(vertical="center")
            if c in (6, 7, 8, 9, 10):
                cell.number_format = '"S/"#,##0.00'

    # Fila totales compras
    total_row_c = r + 1
    r = total_row_c
    ws.cell(row=r, column=5, value="TOTAL COMPRAS").font = _bold_font()
    ws.cell(row=r, column=5).fill = _fill("C8E6C9")
    for c, val in [(6, total_bi_c), (7, total_igv_c), (10, total_cp_c2)]:
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = _bold_font()
        cell.fill = _fill("C8E6C9")
        cell.number_format = '"S/"#,##0.00'
        cell.border = _border_all()

    # ════════════════════════════════════════════════════════════════════════
    # CUADRO DE LIQUIDACIÓN DE IMPUESTOS
    # ════════════════════════════════════════════════════════════════════════
    def _liq_row(ws_target, row_idx, col_a, label, prefix, value, fill_a=None, fill_b=None,
                 font_label=None, font_val=None, num_fmt='"S/"#,##0.00'):
        c_lbl = ws_target.cell(row=row_idx, column=col_a,     value=label)
        c_pre = ws_target.cell(row=row_idx, column=col_a + 1, value=prefix)
        c_val = ws_target.cell(row=row_idx, column=col_a + 2, value=value)

        for c in (c_lbl, c_pre, c_val):
            c.border = _border_all()
        if fill_a:
            c_lbl.fill = fill_a
            c_pre.fill = fill_a
            c_val.fill = fill_a
        if fill_b:
            c_val.fill = fill_b
        if font_label:
            c_lbl.font = font_label
        if font_val:
            c_pre.font  = font_val
            c_val.font  = font_val
        c_val.number_format = num_fmt
        c_val.alignment = Alignment(horizontal="right")

    LIQ_START = r + 3
    LIQ_COL = 1
    r = LIQ_START

    # Título principal
    ws.merge_cells(start_row=r, start_column=LIQ_COL, end_row=r, end_column=LIQ_COL + 2)
    title_cell = ws.cell(row=r, column=LIQ_COL, value="LIQUIDACIÓN DE IMPUESTOS:")
    title_cell.font = Font(bold=True, size=11, color="000000")
    title_cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[r].height = 18

    # Sub-título
    r += 1
    ws.merge_cells(start_row=r, start_column=LIQ_COL, end_row=r, end_column=LIQ_COL + 2)
    sub_cell = ws.cell(row=r, column=LIQ_COL,
                         value=f"IMPUESTOS A PAGAR PERIODO {periodo_fmt[:4]}/{periodo_fmt[4:]}")
    sub_cell.fill = DARK_NAVY
    sub_cell.font = WHITE_FONT
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    sub_cell.border = _border_all()
    ws.row_dimensions[r].height = 22

    r += 1  # línea vacía
    for col in range(LIQ_COL, LIQ_COL + 3):
        ws.cell(row=r, column=col).border = _border_all()

    # Fórmulas de liquidación referenciando las filas calculadas
    end_v = max(header_v_row + 1, total_row_v - 1)
    end_c = max(r_compras_hdr + 1, total_row_c - 1)

    r += 1
    r_ventas_liq = r
    _liq_row(ws, r, LIQ_COL, "TOTAL VENTAS", "S/", f"=SUM(J{header_v_row+1}:J{end_v})",
             font_label=BOLD_FONT, font_val=BOLD_FONT)

    r += 1
    r_compras_liq = r
    _liq_row(ws, r, LIQ_COL, "TOTAL COMPRAS", "S/", f"=SUM(J{r_compras_hdr+1}:J{end_c})",
             font_label=BOLD_FONT, font_val=BOLD_FONT)

    r += 1  # separador
    for col in range(LIQ_COL, LIQ_COL + 3):
        ws.cell(row=r, column=col).border = _border_all()

    r += 1
    r_renta = r
    _liq_row(ws, r, LIQ_COL, "RENTA MYPE 1%", "S/", f"=C{r_ventas_liq}*0.01",
             font_label=BOLD_FONT, font_val=BOLD_FONT)

    r += 1
    r_igv_ventas = r
    _liq_row(ws, r, LIQ_COL, "IGV de ventas", "S/", f"=SUM(G{header_v_row+1}:G{end_v})",
             font_label=NORMAL_FONT, font_val=NORMAL_FONT)

    r += 1
    r_credito = r
    # El crédito fiscal es el IGV de Compras, es decir, el total de la columna G en la tabla COMPRAS
    _liq_row(ws, r, LIQ_COL, "IGV de compras", "-S/", f"=G{total_row_c}",
             font_label=NORMAL_FONT, font_val=NORMAL_FONT)

    r += 1
    r_igv_pagar = r
    _liq_row(ws, r, LIQ_COL, "IGV A PAGAR", "S/", f"=MAX(0, C{r_igv_ventas}-C{r_credito})",
             font_label=BOLD_FONT, font_val=BOLD_FONT,
             num_fmt='"S/"#,##0.00')

    r += 1  # separador
    for col in range(LIQ_COL, LIQ_COL + 3):
        ws.cell(row=r, column=col).border = _border_all()

    r += 1
    r_total_pagar = r
    _liq_row(ws, r, LIQ_COL, "TOTAL A PAGAR", "S/", f"=C{r_renta}+C{r_igv_pagar}",
             fill_a=YELLOW_FILL,
             font_label=Font(bold=True, size=11),
             font_val=Font(bold=True, size=11))

    r += 1
    r_margen = r
    r_utilidad = r + 1
    _liq_row(ws, r, LIQ_COL, "MARGEN DE UTILIDAD BRUTA:", "", f"=IF(C{r_ventas_liq}>0, C{r_utilidad}/C{r_ventas_liq}, 0)",
             font_label=BOLD_FONT, font_val=BOLD_FONT, num_fmt="0.00%")

    r += 1
    _liq_row(ws, r, LIQ_COL, "UTILIDAD:", "S/", f"=C{r_ventas_liq}-C{r_compras_liq}",
             font_label=BOLD_FONT, font_val=BOLD_FONT)

    # Ancho de columnas unificado para la hoja completa
    col_widths = [14, 8, 12, 14, 38, 14, 12, 12, 12, 13, 7]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # ── Guardar y devolver ───────────────────────────────────────────────────
    filename = f"Preliminar_{req.ruc}_{req.periodo}.xlsx"
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/excel/{cliente_id}/{periodo}")
def export_excel(cliente_id: str, periodo: str):
    """Exporta las compras y ventas enriquecidas a Excel."""
    import pandas as pd
    supabase = get_supabase()

    # Obtener el cliente para el nombre de archivo
    res_cli = supabase.table("clientes").select("razon_social, ruc").eq("id", cliente_id).execute()
    if not res_cli.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    ruc = res_cli.data[0]["ruc"]
    razon_social = res_cli.data[0]["razon_social"].replace(" ", "_")

    # Obtener compras
    res_compras = fetch_all_records("sire_preliminar_compras", supabase, "*", {"cliente_id": cliente_id, "periodo": periodo})
    df_compras = pd.DataFrame(res_compras.data)
    if not df_compras.empty and "created_at" in df_compras.columns:
        df_compras = df_compras.drop(columns=["created_at", "cliente_id", "id", "error_log"], errors="ignore")

    # Obtener ventas
    res_ventas = fetch_all_records("sire_preliminar_ventas", supabase, "*", {"cliente_id": cliente_id, "periodo": periodo})
    df_ventas = pd.DataFrame(res_ventas.data)
    if not df_ventas.empty and "created_at" in df_ventas.columns:
        df_ventas = df_ventas.drop(columns=["created_at", "cliente_id", "id", "error_log"], errors="ignore")

    # Generar Excel en memoria
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        if df_compras.empty:
            pd.DataFrame([{"Mensaje": "Sin registros"}]).to_excel(writer, sheet_name="COMPRAS", index=False)
        else:
            df_compras.to_excel(writer, sheet_name="COMPRAS", index=False)

        if df_ventas.empty:
            pd.DataFrame([{"Mensaje": "Sin registros"}]).to_excel(writer, sheet_name="VENTAS", index=False)
        else:
            df_ventas.to_excel(writer, sheet_name="VENTAS", index=False)

    buf.seek(0)
    filename = f"Preliminar_{ruc}_{periodo}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
