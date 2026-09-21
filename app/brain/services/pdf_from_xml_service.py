"""
PDF from XML Batch Service — Quanta V2

Generates PDF invoices from downloaded SUNAT UBL XML files.
Replaces the slow Playwright-based PDF download from the SUNAT portal
with local generation using the existing invoice template.

This service:
  1. Queries sire_comprobantes_fisicos for records where XML is downloaded
     but PDF is not yet generated.
  2. Reads each XML from disk.
  3. Renders it through the Jinja2 invoice template.
  4. Converts the HTML to PDF using a SHARED Playwright browser instance
     (much faster than opening/closing a browser per file).
  5. Saves the PDF alongside the XML in the same folder structure.
  6. Updates the database with ruta_pdf and estado_pdf = 'DESCARGADO'.

Usage:
    # As a standalone script:
    python app/brain/services/pdf_from_xml_service.py --ruc 20613022571 --periodo 202604

    # Programmatically:
    from app.brain.services.pdf_from_xml_service import generate_pdfs_from_xmls
    import asyncio
    asyncio.run(generate_pdfs_from_xmls(ruc="20613022571", periodo="202604"))
"""

from __future__ import annotations

import asyncio
import io
import os
import sys
import zipfile
from pathlib import Path
from typing import Optional

# Ensure we can import app modules
_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.brain.db.supabase_client import get_supabase
from app.brain.pdf_generator import parse_sunat_xml, env as jinja_env

STORAGE_BUCKET = "comprobantes-fisicos"
_TMP_PDF_DIR = Path(__file__).resolve().parents[1] / "downloads" / "tmp_pdf" / "generated"


async def _batch_html_to_pdf(
    jobs: list[tuple[str, str]],
    *,
    concurrency: int = 1,
) -> dict[str, str | None]:
    """
    Convert multiple HTML strings to PDF files using a SINGLE shared
    Playwright browser instance.

    Args:
        jobs: List of (html_content, output_path) tuples.
        concurrency: Number of parallel browser pages (1 is safest).

    Returns:
        Dict mapping output_path -> None on success, or error string on failure.
    """
    from playwright.async_api import async_playwright

    results: dict[str, str | None] = {}

    if not jobs:
        return results

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for html_content, output_path in jobs:
            try:
                page = await browser.new_page()
                await page.set_content(html_content, wait_until="networkidle")
                await page.pdf(
                    path=output_path,
                    format="A4",
                    print_background=True,
                    margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                )
                await page.close()
                results[output_path] = None  # success
            except Exception as e:
                results[output_path] = str(e)

        await browser.close()

    return results


def _looks_like_xml(raw: bytes) -> bool:
    """
    Cheap sanity check before handing bytes to the XML parser. A handful of
    comprobantes uploaded under a concurrent daily_sync run (fixed in the
    same change as this check - see the tmp_downloads_dir PID fix in
    download_xml_scraper.py) ended up with a PDF's bytes stored under the
    path recorded as ruta_xml. Parsing those as XML doesn't raise cleanly -
    lxml's recover=True mode returns a near-empty tree and the code crashes
    later on a None.find() - so catch it here instead, where the message is
    actually useful.

    IMPORTANT: many genuine SUNAT XMLs start with a UTF-8 BOM (b'\\xef\\xbb\\xbf')
    before '<?xml ...'. bytes.lstrip() only strips ASCII whitespace, not the
    BOM, so it must be stripped explicitly here - without this, perfectly
    valid XMLs get misclassified as corrupt (caught live: a full sweep flagged
    dozens of BOM-prefixed zipped XMLs as "corrupted" when they were fine).
    """
    head = raw.lstrip()
    if head.startswith(b"\xef\xbb\xbf"):
        head = head[3:]
    head = head[:16]
    return head.startswith(b"<?xml") or head.startswith(b"<")


def _extract_xml_from_zip_bytes(raw: bytes) -> Optional[bytes]:
    """If raw is a ZIP, return the first .xml member's bytes; otherwise return raw as-is."""
    buf = io.BytesIO(raw)
    if zipfile.is_zipfile(buf):
        buf.seek(0)
        with zipfile.ZipFile(buf, "r") as z:
            for name in z.namelist():
                if name.lower().endswith(".xml"):
                    return z.read(name)
        return None
    if not _looks_like_xml(raw):
        print(f"  [ERROR] El contenido no es XML (primeros bytes: {raw[:12]!r}) - dato corrupto, se omite")
        return None
    return raw


def _load_xml_bytes(supabase, ruta_xml: str) -> Optional[bytes]:
    """
    Read the comprobante's XML, from wherever it actually lives.

    ruta_xml is either a leftover local disk path (only ever valid inside the
    same container run that downloaded it — Railway's disk is ephemeral) or,
    for anything that made it through sire_bot_orchestrator.py's upload step,
    a path inside the 'comprobantes-fisicos' Storage bucket. Try local first
    since it's cheaper, then fall back to Storage — that fallback is what was
    missing before, which made this whole function silently skip almost
    every comprobante once its ruta_xml pointed at Storage instead of disk.
    """
    local_path = Path(ruta_xml)
    if local_path.exists():
        try:
            return _extract_xml_from_zip_bytes(local_path.read_bytes())
        except Exception as e:
            print(f"  [ERROR] No se pudo leer {ruta_xml} del disco: {e}")
            return None

    try:
        raw = supabase.storage.from_(STORAGE_BUCKET).download(ruta_xml)
    except Exception as e:
        print(f"  [ERROR] XML no encontrado ni en disco ni en Storage ({ruta_xml}): {e}")
        return None
    return _extract_xml_from_zip_bytes(raw)


def _upload_pdf_to_storage(supabase, local_pdf_path: str, cliente_id: str, periodo: str, tipo_libro: str, filename: str) -> Optional[str]:
    """
    Uploads a freshly generated PDF to the same Storage bucket the XMLs live
    in, so it survives past this container's lifetime. Returns the Storage
    path on success, None if the upload failed (caller keeps the local path
    as a same-session-only fallback rather than losing the record entirely).
    """
    try:
        content = Path(local_pdf_path).read_bytes()
        storage_path = f"{cliente_id}/{periodo}/{tipo_libro}/{filename}"
        supabase.storage.from_(STORAGE_BUCKET).upload(
            path=storage_path,
            file=content,
            file_options={"content-type": "application/pdf", "upsert": "true"},
        )
        return storage_path
    except Exception as e:
        print(f"  [WARN] No se pudo subir {local_pdf_path} a Storage: {e}")
        return None


async def generate_pdfs_from_xmls(
    ruc: str | None = None,
    periodo: str | None = None,
    tipo_libro: str | None = None,
    limit: int = 500,
    dry_run: bool = False,
) -> dict:
    """
    Main entry point: finds comprobantes with XML downloaded but no PDF,
    generates PDFs from those XMLs, and updates the database.

    Args:
        ruc: Filter by client RUC (optional).
        periodo: Filter by period like '202604' (optional).
        tipo_libro: Filter by 'COMPRAS' or 'VENTAS' (optional).
        limit: Max number of records to process.
        dry_run: If True, only report what would be done without generating.

    Returns:
        Summary dict with counts of success, errors, skipped.
    """
    supabase = get_supabase()

    print("=" * 60)
    print("  GENERACIÓN DE PDFs DESDE XMLs")
    print(f"  RUC: {ruc or 'todos'}  |  Periodo: {periodo or 'todos'}  |  Libro: {tipo_libro or 'todos'}")
    print("=" * 60)

    # ── 1. Resolve cliente_id ────────────────────────────────────
    cliente_id = None
    if ruc:
        r = supabase.table("clientes").select("id").eq("ruc", ruc).execute()
        if not r.data:
            print(f"Error: No se encontró cliente con RUC {ruc}")
            return {"error": f"Cliente {ruc} no encontrado"}
        cliente_id = r.data[0]["id"]

    # ── 2. Query comprobantes: XML descargado, PDF pendiente ─────
    query = (
        supabase.table("sire_comprobantes_fisicos")
        .select("id, cliente_id, periodo, tipo_libro, ruta_xml, ruta_pdf, ruc_tercero, tipo_cp, serie, numero, clientes!inner(ruc, razon_social)")
        .eq("estado_xml", "DESCARGADO")
        .neq("estado_pdf", "DESCARGADO")
        .not_.is_("ruta_xml", "null")
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)
    if periodo:
        query = query.eq("periodo", periodo)
    if tipo_libro:
        query = query.eq("tipo_libro", tipo_libro.upper())

    response = query.limit(limit).execute()
    records = response.data

    if not records:
        print("No hay comprobantes pendientes de generación de PDF.")
        return {"total": 0, "generated": 0, "errors": 0, "skipped": 0}

    print(f"Encontrados {len(records)} comprobantes con XML listo y sin PDF.\n")

    if dry_run:
        print("[DRY RUN] Se generarían PDFs para los siguientes comprobantes:")
        for r in records[:10]:
            print(f"  - {r['serie']}-{r['numero']} ({r['tipo_libro']}) XML: {r['ruta_xml']}")
        if len(records) > 10:
            print(f"  ... y {len(records) - 10} más.")
        return {"total": len(records), "generated": 0, "errors": 0, "skipped": 0, "dry_run": True}

    # ── 3. Prepare HTML render jobs ──────────────────────────────
    template = jinja_env.get_template("invoice_template.html")
    _TMP_PDF_DIR.mkdir(parents=True, exist_ok=True)
    jobs: list[tuple[str, str]] = []  # (html, output_path)
    job_record_map: list[dict] = []   # parallel list of DB records

    skipped = 0
    parse_errors = 0

    for rec in records:
        # Local temp path keyed by the record's own id - independent of
        # whatever shape ruta_xml has (local leftover path or Storage path),
        # since the previous folder-mirroring logic silently broke as soon
        # as ruta_xml pointed at Storage instead of a real local directory.
        pdf_output = _TMP_PDF_DIR / f"{rec['id']}.pdf"

        xml_bytes = _load_xml_bytes(supabase, rec["ruta_xml"])
        if not xml_bytes:
            print(f"  [SKIP] XML no encontrado ni en disco ni en Storage: {rec['ruta_xml']}")
            skipped += 1
            continue

        data = parse_sunat_xml(xml_bytes)
        if not data:
            print(f"  [ERROR] No se pudo parsear XML de {rec['serie']}-{rec['numero']}")
            parse_errors += 1
            continue

        # Render HTML
        html_content = template.render(data=data)
        jobs.append((html_content, str(pdf_output)))
        job_record_map.append(rec)

    if not jobs:
        print(f"\nNo hay PDFs que generar. Skipped: {skipped}, Errores parse: {parse_errors}")
        return {"total": len(records), "generated": 0, "errors": parse_errors, "skipped": skipped}

    # ── 4. Batch convert HTML → PDF ──────────────────────────────
    print(f"\nGenerando {len(jobs)} PDFs con Playwright (instancia compartida)...")
    results = await _batch_html_to_pdf(jobs)

    # ── 5. Upload each generated PDF to Storage and update database ──
    generated = 0
    gen_errors = 0

    for (html, output_path), rec in zip(jobs, job_record_map):
        error = results.get(output_path)
        if error is None:
            # Success - upload to the same bucket the XMLs live in so the
            # PDF survives past this container's ephemeral disk. Falls back
            # to the local path only if the upload itself fails.
            pdf_filename = f"{rec['serie']}-{rec['numero']}.pdf"
            uploaded_path = _upload_pdf_to_storage(
                supabase, output_path, rec["cliente_id"], rec["periodo"], rec["tipo_libro"], pdf_filename
            )
            stored_path = uploaded_path or output_path

            supabase.table("sire_comprobantes_fisicos").update({
                "ruta_pdf": stored_path,
                "estado_pdf": "DESCARGADO",
            }).eq("id", rec["id"]).execute()

            # Only delete the local temp copy once it's safely in Storage -
            # if the upload failed, ruta_pdf still points at this local file
            # and it needs to stay put for the rest of this container's life.
            if uploaded_path:
                try:
                    os.remove(output_path)
                except OSError:
                    pass

            generated += 1
            print(f"  [OK] {pdf_filename}")
        else:
            gen_errors += 1
            print(f"  [ERROR] {rec['serie']}-{rec['numero']}: {error}")

    total_errors = parse_errors + gen_errors

    print(f"\n{'=' * 60}")
    print(f"  RESUMEN GENERACIÓN DE PDFs")
    print(f"  Generados: {generated}  |  Errores: {total_errors}  |  Saltados: {skipped}")
    print(f"{'=' * 60}")

    return {
        "total": len(records),
        "generated": generated,
        "errors": total_errors,
        "skipped": skipped,
    }


# ── CLI entry point ──────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generar PDFs desde XMLs descargados")
    parser.add_argument("--ruc", type=str, help="RUC del cliente a procesar")
    parser.add_argument("--periodo", type=str, help="Periodo (ej: 202604)")
    parser.add_argument("--tipo_libro", type=str, help="COMPRAS o VENTAS")
    parser.add_argument("--limit", type=int, default=500, help="Máximo de registros")
    parser.add_argument("--dry-run", action="store_true", help="Solo reportar sin generar")
    args = parser.parse_args()

    asyncio.run(
        generate_pdfs_from_xmls(
            ruc=args.ruc,
            periodo=args.periodo,
            tipo_libro=args.tipo_libro,
            limit=args.limit,
            dry_run=args.dry_run,
        )
    )
