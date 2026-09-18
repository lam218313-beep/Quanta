"""Match SIRE data with UBL XML files and extract item descriptions.

Parses UBL 2.1 XML invoices/credit-notes/debit-notes and extracts the
``cbc:Description`` from each ``cac:InvoiceLine`` (or equivalent).  Then
matches those descriptions back to the SIRE TXT rows by key:
  (RUC emisor, tipo, serie, numero)

Usage:
  from brain.sire_xml_matcher import match_xml_descriptions

  desc_map = match_xml_descriptions(
      xml_dir=Path("downloads/xml/202501/purchases"),
      sire_rows=iter_sire_rows(txt_path, "purchases"),
  )
  # desc_map[(ruc, tipo, serie, numero)] -> "Item 1; Item 2; ..."
"""

from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional


# UBL 2.1 namespaces
_NS = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "inv": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cn": "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2",
    "dn": "urn:oasis:names:specification:ubl:schema:xsd:DebitNote-2",
}


import zipfile

def _extract_from_xml(xml_path: Path) -> Optional[dict]:
    """Extract key fields and item descriptions from a UBL XML or ZIP file."""
    try:
        if zipfile.is_zipfile(xml_path):
            with zipfile.ZipFile(xml_path, "r") as z:
                for name in z.namelist():
                    if name.lower().endswith(".xml"):
                        xml_bytes = z.read(name)
                        info = _extract_from_xml_string(xml_bytes)
                        if info:
                            return info
            return None
        else:
            content = xml_path.read_bytes()
            return _extract_from_xml_string(content)
    except Exception as e:
        print(f"Error parsing {xml_path}: {e}")
        return None

def _extract_from_xml_string(xml_bytes: bytes) -> Optional[dict]:
    """Extract key fields and item descriptions from UBL XML bytes."""
    try:
        root = ET.fromstring(xml_bytes)
    except Exception:
        return None

    # Detect root namespace to handle Invoice / CreditNote / DebitNote
    root_tag = root.tag
    ns_map = dict(_NS)

    # Try to extract the document ID (e.g. "F001-123")
    doc_id = None
    for ns_prefix in ("inv", "cn", "dn", ""):
        id_path = f"{{{ns_map.get(ns_prefix, '')}}}ID" if ns_prefix else "ID"
        el = root.find(f"cbc:ID", ns_map) if ns_prefix == "" else root.find(f"cbc:ID", ns_map)
        if el is None:
            # Try without namespace
            el = root.find(".//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
        if el is not None and el.text:
            doc_id = el.text.strip()
            break

    # Extract supplier RUC
    ruc_emisor = ""
    supplier_paths = [
        ".//cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID",
        ".//cac:AccountingSupplierParty//cbc:CompanyID",
    ]
    for sp in supplier_paths:
        el = root.find(sp, ns_map)
        if el is not None and el.text:
            ruc_emisor = el.text.strip()
            break

    # Parse document ID into serie + numero
    serie = ""
    numero = ""
    if doc_id and "-" in doc_id:
        parts = doc_id.split("-", 1)
        serie = parts[0]
        numero = parts[1]

    # Detect document type from InvoiceTypeCode or similar
    tipo = ""
    type_el = root.find(".//cbc:InvoiceTypeCode", ns_map)
    if type_el is not None and type_el.text:
        tipo = type_el.text.strip()
    else:
        # CreditNote / DebitNote don't always have InvoiceTypeCode
        if "CreditNote" in root_tag:
            tipo = "07"
        elif "DebitNote" in root_tag:
            tipo = "08"

    # Extract line descriptions
    descriptions: list[str] = []

    # InvoiceLine / CreditNoteLine / DebitNoteLine
    line_tags = [
        ".//cac:InvoiceLine",
        ".//cac:CreditNoteLine",
        ".//cac:DebitNoteLine",
    ]
    for lt in line_tags:
        for line_el in root.findall(lt, ns_map):
            # cac:Item/cbc:Description
            desc_el = line_el.find("cac:Item/cbc:Description", ns_map)
            if desc_el is not None and desc_el.text:
                descriptions.append(desc_el.text.strip())
            else:
                # Fallback: try cbc:Description directly under line
                desc_el = line_el.find("cbc:Description", ns_map)
                if desc_el is not None and desc_el.text:
                    descriptions.append(desc_el.text.strip())
                else:
                    # Try cac:Item/cbc:Name
                    name_el = line_el.find("cac:Item/cbc:Name", ns_map)
                    if name_el is not None and name_el.text:
                        descriptions.append(name_el.text.strip())

    # Detect Detracción by searching all text content
    xml_text = "".join(root.itertext()).upper()
    tiene_detraccion = "NO"
    if "DETRACCION" in xml_text or "DETRACCIÓN" in xml_text or "SPOT" in xml_text:
        tiene_detraccion = "SÍ"

    return {
        "ruc_emisor": ruc_emisor,
        "tipo": tipo,
        "serie": serie,
        "numero": numero,
        "doc_id": doc_id or "",
        "descriptions": descriptions,
        "detraccion": tiene_detraccion,
    }


def _normalize_numero(n: str) -> str:
    """Strip leading zeros for comparison."""
    stripped = n.lstrip("0")
    return stripped if stripped else "0"


def match_xml_descriptions(
    xml_dir: Path,
    *,
    recursive: bool = True,
) -> dict[tuple[str, str, str, str], dict]:
    """Scan a directory of XML files and build a lookup dict.

    Returns:
      { (ruc_emisor, tipo, serie, numero) : {"descripcion": "desc1; desc2", "detraccion": "SÍ"} }
    """
    result: dict[tuple[str, str, str, str], dict] = {}

    import zipfile
    
    if not xml_dir.exists():
        return result

    for ext in ("*.xml", "*.zip"):
        pattern = f"**/{ext}" if recursive else ext
        for file_path in xml_dir.glob(pattern):
            if file_path.name.startswith("_debug") or "debug" in str(file_path.parent).lower():
                continue

            infos = []
            if file_path.suffix.lower() == ".zip":
                try:
                    import io
                    def _process_zip(z: zipfile.ZipFile, infos_list: list):
                        for name in z.namelist():
                            if name.lower().endswith(".xml"):
                                xml_bytes = z.read(name)
                                info = _extract_from_xml_string(xml_bytes)
                                if info:
                                    infos_list.append(info)
                            elif name.lower().endswith(".zip"):
                                try:
                                    inner_bytes = z.read(name)
                                    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner_z:
                                        _process_zip(inner_z, infos_list)
                                except zipfile.BadZipFile:
                                    pass

                    with zipfile.ZipFile(file_path, "r") as z:
                        _process_zip(z, infos)
                except zipfile.BadZipFile:
                    pass
            else:
                info = _extract_from_xml(file_path)
                if info:
                    infos.append(info)

            for info in infos:
                if not info or not info["ruc_emisor"]:
                    continue

                key = (
                    info["ruc_emisor"],
                    info["tipo"],
                    info["serie"],
                    _normalize_numero(info["numero"]),
                )
                desc_text = "; ".join(info["descriptions"]) if info["descriptions"] else ""
                if desc_text or info["detraccion"] == "SÍ":
                    result[key] = {
                        "descripcion": desc_text,
                        "detraccion": info["detraccion"],
                    }

    return result


def enrich_sire_data(
    sire_rows: list,
    xml_dir: Path,
) -> list[tuple]:
    """Match SIRE rows with XML descriptions and return enriched data.

    Parameters
    ----------
    sire_rows : list of SireRow objects (from sire_xml_scrape_cli.iter_sire_rows)
    xml_dir : Path to directory with downloaded XML files

    Returns
    -------
    List of (sire_row, description_text) tuples
    """
    xml_map = match_xml_descriptions(xml_dir)

    enriched = []
    matched = 0
    for row in sire_rows:
        key = (
            row.ruc_emisor,
            row.tipo,
            row.serie,
            _normalize_numero(row.numero),
        )
        desc = xml_map.get(key, "")
        if desc:
            matched += 1
        enriched.append((row, desc))

    print(f"📊 XML Match: {matched}/{len(sire_rows)} comprobantes matched with XML descriptions")
    return enriched


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python sire_xml_matcher.py <xml_dir>")
        print("  Scans XML files and prints extracted descriptions.")
        sys.exit(1)

    xml_dir = Path(sys.argv[1])
    desc_map = match_xml_descriptions(xml_dir)
    print(f"Found {len(desc_map)} comprobantes with descriptions:\n")
    for key, desc in sorted(desc_map.items()):
        print(f"  {key[0]}-{key[1]}-{key[2]}-{key[3]}: {desc[:100]}")
