"""Batch-download CPE XML/PDF from SUNAT portal using Playwright cookies.

This uses the existing semi-manual login approach:
1) Run: python brain/automation_scraper.py
   - Log in manually
   - Navigate the menu to generate cookies
   - It will save cookies to brain/sunat_session.json
2) Then run this script against a SIRE TXT file to download XMLs into folders by period.

Example:
  python sire_xml_scrape_cli.py \\
      --sire-txt downloads/sire/20600373065/202501/purchases/...-propuesta.txt \\
      --book purchases --limit 5

Outputs:
  downloads/xml/<YYYYMM>/<book>/<rucEmisor>-<tipo>-<serie>-<numero>.xml (or .pdf)
  downloads/xml/<YYYYMM>/<book>/scrape_results.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Optional

# Ensure project root is in sys.path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))


# ---------------------------------------------------------------------------
# SIRE TXT parser
# ---------------------------------------------------------------------------

def _split_pipe(line: str) -> list[str]:
    return line.rstrip("\n").rstrip("\r").split("|")


def _norm(s: str) -> str:
    # Strip BOM + normalize whitespace + lowercase
    cleaned = (s or "").replace("\ufeff", "").strip().lower().replace("/", " ")
    return " ".join(cleaned.split())


def _find_col(headers: list[str], *candidates: str) -> Optional[int]:
    norm_headers = [_norm(h) for h in headers]
    for c in candidates:
        key = _norm(c)
        try:
            return norm_headers.index(key)
        except ValueError:
            continue
    return None


def _looks_like_ruc(value: str) -> bool:
    v = (value or "").strip()
    return len(v) == 11 and v.isdigit() and (v.startswith("10") or v.startswith("20"))


class SireRow:
    __slots__ = ("period", "book", "ruc_emisor", "tipo", "serie", "numero",
                 "importe", "fecha", "car_sunat")

    def __init__(self, *, period, book, ruc_emisor, tipo, serie, numero, importe, fecha, car_sunat):
        self.period = period
        self.book = book
        self.ruc_emisor = ruc_emisor
        self.tipo = tipo
        self.serie = serie
        self.numero = numero
        self.importe = importe
        self.fecha = fecha
        self.car_sunat = car_sunat


def iter_sire_rows(txt_path: Path, book: str) -> list[SireRow]:
    """Parse a SIRE TXT export into a list of SireRow objects."""
    with txt_path.open("r", encoding="utf-8", errors="replace") as f:
        header_line = f.readline()
        if not header_line:
            return []
        headers = _split_pipe(header_line)

        idx_period = _find_col(headers, "Periodo")
        idx_car = _find_col(headers, "CAR SUNAT")
        idx_fecha = _find_col(headers, "Fecha de emisión", "Fecha de emision")
        idx_tipo = _find_col(headers, "Tipo CP/Doc.", "Tipo CP/Doc")
        idx_serie = _find_col(headers, "Serie del CDP")
        idx_num = _find_col(headers, "Nro CP o Doc. Nro Inicial (Rango)", "Nro CP o Doc. Nro Inicial")
        idx_total = _find_col(headers, "Total CP")

        idx_ruc_col = _find_col(headers, "RUC", "Ruc")
        idx_doc_id = _find_col(headers, "Nro Doc Identidad")
        idx_tipo_doc_id = _find_col(headers, "Tipo Doc Identidad")

        missing = [
            ("Periodo", idx_period),
            ("CAR SUNAT", idx_car),
            ("Fecha de emisión", idx_fecha),
            ("Tipo CP/Doc", idx_tipo),
            ("Serie", idx_serie),
            ("Número", idx_num),
            ("Total", idx_total),
        ]
        missing = [name for name, idx in missing if idx is None]
        if missing:
            raise SystemExit(f"Missing required columns in SIRE TXT header: {missing}")

        rows: list[SireRow] = []
        for line in f:
            if not line.strip():
                continue
            parts = _split_pipe(line)

            def get(i: Optional[int]) -> str:
                if i is None:
                    return ""
                return (parts[i] if i < len(parts) else "").strip()

            period = get(idx_period)
            car_sunat = get(idx_car)
            fecha = get(idx_fecha)
            tipo = get(idx_tipo)
            serie = get(idx_serie)
            numero = get(idx_num)
            importe = get(idx_total)

            if book == "purchases":
                tipo_doc = get(idx_tipo_doc_id)
                doc_id = get(idx_doc_id)
                ruc_emisor = doc_id if tipo_doc == "6" and _looks_like_ruc(doc_id) else ""
            else:
                ruc_emisor = get(idx_ruc_col)

            if not period or len(period) != 6 or not period.isdigit():
                continue
            if not (tipo and serie and numero and fecha and importe and ruc_emisor):
                continue

            rows.append(
                SireRow(
                    period=period,
                    book=book,
                    ruc_emisor=ruc_emisor,
                    tipo=tipo,
                    serie=serie,
                    numero=numero,
                    importe=importe,
                    fecha=fecha,
                    car_sunat=car_sunat,
                )
            )

        return rows


# ---------------------------------------------------------------------------
# Results CSV writer
# ---------------------------------------------------------------------------

def write_results_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["status", "ruc_emisor", "tipo", "serie", "numero", "period", "book", "path", "error"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download CPE XMLs/PDFs from SUNAT portal (from SIRE TXT)",
    )
    parser.add_argument("--sire-txt", required=True,
                        help="Path to SIRE TXT (proposal/preliminar export)")
    parser.add_argument("--book", choices=["purchases", "sales"], required=True,
                        help="Which SIRE book the TXT is from")
    parser.add_argument("--outdir", default="downloads/xml",
                        help="Base output directory")
    parser.add_argument("--prefer", choices=["xml", "pdf", "either"], default="xml",
                        help="Prefer downloading XML or PDF")
    parser.add_argument("--headless", action="store_true",
                        help="Run Chromium headless")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limit number of documents (0 = no limit)")
    parser.add_argument("--no-skip-existing", action="store_true",
                        help="Do not skip already downloaded files")

    args = parser.parse_args()

    txt_path = Path(args.sire_txt).expanduser().resolve()
    if not txt_path.exists():
        raise SystemExit(f"SIRE TXT not found: {txt_path}")

    sire_rows = []
    if txt_path.is_dir():
        print(f"📂 Scanning directory for SIRE TXT files: {txt_path}")
        txt_files = list(txt_path.glob("*.txt"))
        if not txt_files:
            raise SystemExit(f"No .txt files found in directory: {txt_path}")
        for t in txt_files:
            print(f"   Reading: {t.name}")
            sire_rows.extend(iter_sire_rows(t, book=args.book))
    else:
        print(f"📂 Reading SIRE TXT: {txt_path}")
        sire_rows.extend(iter_sire_rows(txt_path, book=args.book))
        
    if not sire_rows:
        print("No rows found / nothing to scrape")
        return 0

    print(f"   Found {len(sire_rows)} comprobantes")

    # Deduplicate by (period, ruc, tipo, serie, numero)
    seen: set[tuple[str, str, str, str, str]] = set()
    unique_rows: list[SireRow] = []
    for r in sire_rows:
        key = (r.period, r.ruc_emisor, r.tipo, r.serie, r.numero)
        if key in seen:
            continue
        seen.add(key)
        unique_rows.append(r)

    print(f"   Unique: {len(unique_rows)} (after dedup)")

    from brain.download_xml_scraper import CpeQuery, run_batch

    queries = [
        CpeQuery(
            ruc_emisor=r.ruc_emisor,
            tipo=r.tipo,
            serie=r.serie,
            numero=r.numero,
            importe=r.importe,
            fecha=r.fecha,
            period=r.period,
            book=r.book,
            car_sunat=r.car_sunat,
        )
        for r in unique_rows
    ]

    results = asyncio_run(
        run_batch(
            queries,
            outdir=str(Path(args.outdir).expanduser().resolve()),
            prefer=args.prefer,
            headless=bool(args.headless),
            skip_existing=not bool(args.no_skip_existing),
            limit=int(args.limit),
        )
    )

    # Write results CSV per period
    for period in sorted({r["period"] for r in results if r.get("period")}):
        period_results = [x for x in results if x.get("period") == period]
        csv_path = Path(args.outdir) / period / args.book / "scrape_results.csv"
        write_results_csv(csv_path, period_results)

    # Summary
    ok = sum(1 for r in results if r.get("status") == "ok")
    skipped = sum(1 for r in results if r.get("status") == "skipped")
    not_found = sum(1 for r in results if r.get("status") == "not_found")
    err = sum(1 for r in results if r.get("status") == "error")

    print("\n=== Scrape Summary ===")
    print(f"ok: {ok}")
    print(f"skipped: {skipped}")
    print(f"not_found: {not_found}")
    print(f"err: {err}")

    # --- AUTOMATIC EXCEL GENERATION ---
    print("\n📊 Generating Excel files with XML data...")
    from brain.sire_txt_to_excel import convert_one
    
    # We iterate over the period folders to find the XML directories we used
    for period in sorted({r["period"] for r in results if r.get("period")}):
        xml_dir = Path(args.outdir).expanduser().resolve() / period / args.book
        
        # We process each TXT file that was requested
        txt_files_to_convert = []
        if txt_path.is_dir():
            txt_files_to_convert = list(txt_path.glob("*.txt"))
        else:
            txt_files_to_convert = [txt_path]
            
        for t in txt_files_to_convert:
            xlsx_path = t.with_suffix(".xlsx")
            sheet_name = f"{args.book}_{period}"[:31]
            try:
                print(f"   Converting: {t.name} -> {xlsx_path.name}")
                convert_one(
                    t,
                    xlsx_path,
                    encoding="utf-8",
                    overwrite=True,
                    has_header=True,
                    sheet_name=sheet_name,
                    add_concept=True,
                    xml_dir=xml_dir,
                )
            except Exception as e:
                print(f"   ❌ Error converting {t.name}: {e}")

    print("\n✅ All done!")
    return 0 if err == 0 else 2


def asyncio_run(awaitable):
    import asyncio
    return asyncio.run(awaitable)


if __name__ == "__main__":
    raise SystemExit(main())
