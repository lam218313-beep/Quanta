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


def _read_xml_bytes(xml_path: Path) -> Optional[bytes]:
    """Read XML bytes from a file or from inside a ZIP archive."""
    try:
        if zipfile.is_zipfile(xml_path):
            with zipfile.ZipFile(xml_path, "r") as z:
                for name in z.namelist():
                    if name.lower().endswith(".xml"):
                        return z.read(name)
            return None
        else:
            return xml_path.read_bytes()
    except Exception as e:
        print(f"  [ERROR] No se pudo leer {xml_path}: {e}")
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
    jobs: list[tuple[str, str]] = []  # (html, output_path)
    job_record_map: list[dict] = []   # parallel list of DB records

    skipped = 0
    parse_errors = 0

    for rec in records:
        xml_path = Path(rec["ruta_xml"])

        if not xml_path.exists():
            print(f"  [SKIP] XML no encontrado en disco: {xml_path}")
            skipped += 1
            continue

        # Determine output PDF path (same directory structure, in /pdf/ subfolder)
        # Current XML path: downloads/xml/{client}/{period}/{book}/xml/{file}.xml
        # Target PDF path:  downloads/xml/{client}/{period}/{book}/pdf/{file}.pdf
        xml_parent = xml_path.parent  # .../xml/
        book_dir = xml_parent.parent  # .../{book}/
        pdf_dir = book_dir / "pdf"
        pdf_dir.mkdir(parents=True, exist_ok=True)

        pdf_filename = xml_path.stem + ".pdf"
        pdf_output = pdf_dir / pdf_filename

        # Skip if PDF already exists on disk
        if pdf_output.exists():
            print(f"  [SKIP] PDF ya existe: {pdf_output.name}")
            # Still update DB to mark it as downloaded
            supabase.table("sire_comprobantes_fisicos").update({
                "ruta_pdf": str(pdf_output),
                "estado_pdf": "DESCARGADO",
            }).eq("id", rec["id"]).execute()
            skipped += 1
            continue

        # Read and parse XML
        xml_bytes = _read_xml_bytes(xml_path)
        if not xml_bytes:
            print(f"  [ERROR] No se pudo leer XML: {xml_path.name}")
            parse_errors += 1
            continue

        data = parse_sunat_xml(xml_bytes)
        if not data:
            print(f"  [ERROR] No se pudo parsear XML: {xml_path.name}")
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

    # ── 5. Update database ───────────────────────────────────────
    generated = 0
    gen_errors = 0

    for (html, output_path), rec in zip(jobs, job_record_map):
        error = results.get(output_path)
        if error is None:
            # Success
            supabase.table("sire_comprobantes_fisicos").update({
                "ruta_pdf": output_path,
                "estado_pdf": "DESCARGADO",
            }).eq("id", rec["id"]).execute()
            generated += 1
            print(f"  [OK] {Path(output_path).name}")
        else:
            gen_errors += 1
            print(f"  [ERROR] {Path(output_path).name}: {error}")

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
