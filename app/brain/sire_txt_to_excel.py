"""Convert SUNAT SIRE TXT (pipe-delimited) to Excel .xlsx.

This is a local/terminal utility: no backend, no frontend.

Input format:
- First line is expected to be header with columns separated by '|'
- Next lines are data rows separated by '|'

Examples:
  python brain/sire_txt_to_excel.py --input downloads/sire/20600373065/202501/purchases/file.txt
  python brain/sire_txt_to_excel.py --input-dir downloads/sire --recursive

By default, writes an .xlsx next to each .txt.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Optional


def _iter_txt_files(input_path: Optional[Path], input_dir: Optional[Path], recursive: bool) -> list[Path]:
    files: list[Path] = []

    if input_path is not None:
        if not input_path.exists() or not input_path.is_file():
            raise SystemExit(f"--input not found or not a file: {input_path}")
        files.append(input_path)
        return files

    if input_dir is None:
        raise SystemExit("Provide either --input or --input-dir")

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"--input-dir not found or not a directory: {input_dir}")

    pattern = "**/*.txt" if recursive else "*.txt"
    return sorted([p for p in input_dir.glob(pattern) if p.is_file()])


def _split_pipe(line: str) -> list[str]:
    # Keep trailing empty fields.
    return line.rstrip("\n").rstrip("\r").split("|")


def _safe_output_path(
    txt_file: Path,
    outdir: Optional[Path],
    input_dir: Optional[Path],
) -> Path:
    if outdir is None:
        return txt_file.with_suffix(".xlsx")

    outdir = outdir.resolve()
    if input_dir is not None:
        try:
            rel = txt_file.resolve().relative_to(input_dir.resolve())
        except Exception:
            rel = txt_file.name
    else:
        rel = txt_file.name

    if isinstance(rel, Path):
        return (outdir / rel).with_suffix(".xlsx")
    return (outdir / str(rel)).with_suffix(".xlsx")


def convert_one(
    txt_file: Path,
    xlsx_file: Path,
    *,
    encoding: str,
    overwrite: bool,
    has_header: bool,
    sheet_name: str,
    add_concept: bool,
    xml_dir: Optional[Path] = None,
) -> None:
    try:
        from openpyxl import Workbook
    except Exception as e:
        raise SystemExit(
            "Missing dependency 'openpyxl'. Install it with: python -m pip install openpyxl"
        ) from e

    if xlsx_file.exists() and not overwrite:
        print(f"Skip (exists): {xlsx_file}")
        return

    xlsx_file.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook(write_only=False)
    ws = wb.active
    ws.title = sheet_name

    def _normalize_header(h: str) -> str:
        return " ".join((h or "").strip().lower().replace("/", " ").split())

    def _get_col_index(headers: list[str], want: Iterable[str]) -> Optional[int]:
        norm = [_normalize_header(h) for h in headers]
        for key in want:
            k = _normalize_header(key)
            try:
                return norm.index(k)
            except ValueError:
                continue
        return None

    def _build_concept(headers: list[str], row: list[str]) -> str:
        if not headers or not row:
            return ""

        idx_name = _get_col_index(
            headers,
            [
                "Apellidos Nombres/ Razón  Social",
                "Apellidos Nombres/ Razón Social",
                "Razon Social",
                "Razón social",
                "Razon social",
            ],
        )
        idx_tipo = _get_col_index(headers, ["Tipo CP/Doc.", "Tipo CP/Doc", "Tipo Doc."])
        idx_serie = _get_col_index(headers, ["Serie del CDP", "Serie del CDP ", "Serie"])
        idx_num = _get_col_index(
            headers,
            [
                "Nro CP o Doc. Nro Inicial (Rango)",
                "Nro CP o Doc. Nro Inicial (Rango)",
                "Nro CP o Doc. Nro Inicial",
                "Nro CP o Doc.",
                "Nro CP o Doc",
            ],
        )
        idx_fecha = _get_col_index(headers, ["Fecha de emisión", "Fecha de emision"])

        def get(i: Optional[int]) -> str:
            if i is None:
                return ""
            return (row[i] if i < len(row) else "").strip()

        name = get(idx_name)
        tipo = get(idx_tipo)
        serie = get(idx_serie)
        num = get(idx_num)
        fecha = get(idx_fecha)

        doc = "".join(
            [
                (tipo + " ") if tipo else "",
                (serie + "-") if serie and num else (serie if serie else ""),
                num,
            ]
        ).strip(" -")

        parts = [p for p in [name, doc, fecha] if p]
        return " | ".join(parts)

    # Load XML descriptions if xml_dir is provided
    xml_desc_map: dict = {}
    if xml_dir and xml_dir.exists():
        try:
            from brain.sire_xml_matcher import match_xml_descriptions
            xml_desc_map = match_xml_descriptions(xml_dir, recursive=True)
            print(f"   📦 Loaded {len(xml_desc_map)} XML descriptions from {xml_dir}")
        except Exception as e:
            print(f"   ⚠️ Could not load XML descriptions: {e}")

    add_xml_desc = bool(xml_desc_map)

    with txt_file.open("r", encoding=encoding, errors="replace") as f:
        first = f.readline()
        if not first:
            print(f"Skip (empty): {txt_file}")
            return

        if has_header:
            headers = _split_pipe(first)
            if add_concept:
                headers = headers + ["CONCEPTO"]
            if add_xml_desc:
                headers = headers + ["DESCRIPCION_XML", "TIENE_DETRACCION"]
            ws.append(headers)
        else:
            first_row = _split_pipe(first)
            headers = [f"COL_{i+1}" for i in range(len(first_row))]
            if add_concept:
                headers = headers + ["CONCEPTO"]
            if add_xml_desc:
                headers = headers + ["DESCRIPCION_XML", "TIENE_DETRACCION"]
            ws.append(headers)
            extras = []
            if add_concept:
                extras.append("")
            if add_xml_desc:
                extras.extend(["", ""])
            ws.append(first_row + extras)

        max_cols = len(headers)

        # For concept computation, we need headers without the added columns
        extra_count = (1 if add_concept else 0) + (2 if add_xml_desc else 0)
        base_headers = headers[:-extra_count] if extra_count else headers

        # Find column indices for XML matching
        xml_idx_ruc = _get_col_index(base_headers, ["Nro Doc Identidad", "RUC", "Ruc"])
        xml_idx_tipo_doc = _get_col_index(base_headers, ["Tipo Doc Identidad"])
        xml_idx_tipo = _get_col_index(base_headers, ["Tipo CP/Doc.", "Tipo CP/Doc"])
        xml_idx_serie = _get_col_index(base_headers, ["Serie del CDP"])
        xml_idx_num = _get_col_index(
            base_headers,
            ["Nro CP o Doc. Nro Inicial (Rango)", "Nro CP o Doc. Nro Inicial"],
        )

        def _get_xml_data(row: list[str]) -> dict:
            if not xml_desc_map:
                return {"descripcion": "", "detraccion": ""}

            def _g(i: Optional[int]) -> str:
                if i is None:
                    return ""
                return (row[i] if i < len(row) else "").strip()

            # Determine RUC emisor
            tipo_doc = _g(xml_idx_tipo_doc)
            ruc = _g(xml_idx_ruc)
            if tipo_doc and tipo_doc != "6":
                ruc = ""  # Not a RUC

            tipo = _g(xml_idx_tipo)
            serie = _g(xml_idx_serie)
            numero = _g(xml_idx_num)
            norm_num = numero.lstrip("0") or "0"

            return xml_desc_map.get((ruc, tipo, serie, norm_num), {"descripcion": "", "detraccion": ""})

        for line in f:
            if not line.strip():
                continue
            row = _split_pipe(line)
            extras = []
            if add_concept:
                extras.append(_build_concept(base_headers, row))
            if add_xml_desc:
                data = _get_xml_data(row)
                extras.extend([data.get("descripcion", ""), data.get("detraccion", "")])
            ws.append(row + extras)

    # Basic usability: freeze header, enable filter
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    wb.save(xlsx_file)
    print(f"Wrote: {xlsx_file}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert SIRE .txt to Excel .xlsx")
    parser.add_argument("--input", type=str, default="", help="Single .txt file")
    parser.add_argument("--input-dir", type=str, default="", help="Directory to scan for .txt")
    parser.add_argument("--recursive", action="store_true", help="Scan input-dir recursively")
    parser.add_argument("--outdir", type=str, default="", help="Output base directory")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing .xlsx")
    parser.add_argument("--encoding", type=str, default="utf-8", help="Input text encoding")
    parser.add_argument("--no-header", action="store_true", help="Treat first line as data")
    parser.add_argument("--sheet-name", type=str, default="SIRE", help="Excel sheet name")
    parser.add_argument(
        "--add-concept",
        action="store_true",
        help=(
            "Add a computed CONCEPTO column (glosa) based on name + document + date. "
            "Note: SIRE TXT does not include item-level descriptions."
        ),
    )
    parser.add_argument(
        "--xml-dir",
        type=str,
        default="",
        help=(
            "Path to directory with downloaded UBL XML files. "
            "Enables automatic DESCRIPCION_XML column with real item descriptions."
        ),
    )

    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve() if args.input else None
    input_dir = Path(args.input_dir).expanduser().resolve() if args.input_dir else None
    outdir = Path(args.outdir).expanduser().resolve() if args.outdir else None
    xml_dir = Path(args.xml_dir).expanduser().resolve() if args.xml_dir else None

    files = _iter_txt_files(input_path, input_dir, args.recursive)
    if not files:
        print("No .txt files found")
        return 0

    for txt in files:
        xlsx = _safe_output_path(txt, outdir, input_dir)
        convert_one(
            txt,
            xlsx,
            encoding=args.encoding,
            overwrite=bool(args.overwrite),
            has_header=not bool(args.no_header),
            sheet_name=args.sheet_name,
            add_concept=bool(args.add_concept),
            xml_dir=xml_dir,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
