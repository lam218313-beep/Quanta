"""
Carga del Plan Contable General Empresarial (PCGE) en Supabase.

Lee el archivo plancontable.md, extrae los códigos y descripciones de cada
cuenta contable, y los inserta en la tabla `plan_contable` de Supabase.

Uso:
    python app/brain/db/load_pcge.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _ensure_import_path() -> None:
    root = str(_repo_root())
    if root not in sys.path:
        sys.path.insert(0, root)


# Líneas a ignorar (cabeceras de página, títulos, etc.)
NOISE_PATTERNS = [
    re.compile(r"^PLAN CONTABLE GENERAL", re.IGNORECASE),
    re.compile(r"^CATÁLOGO DE CUENTAS", re.IGNORECASE),
    re.compile(r"^ELEMENTO\s+\d+:", re.IGNORECASE),
    re.compile(r"^Contabilidad Básica", re.IGNORECASE),
    re.compile(r"^\s*$"),  # líneas vacías
]

# Patrón principal: código numérico seguido de descripción
ACCOUNT_RE = re.compile(r"^(\d{2,6})\s+(.+)$")


def parse_plan_contable(md_path: Path) -> list[dict]:
    """
    Parsea el archivo plancontable.md y devuelve una lista de dicts con:
    - codigo: str
    - descripcion: str
    - nivel: int (cantidad de dígitos del código)
    - elemento: str (primer dígito del código)
    """
    records: list[dict] = []
    seen_codigos: set[str] = set()

    with open(md_path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            # Saltar líneas de ruido
            if any(p.search(line) for p in NOISE_PATTERNS):
                continue

            match = ACCOUNT_RE.match(line)
            if not match:
                continue

            codigo = match.group(1).strip()
            descripcion = match.group(2).strip()

            # Limpiar la descripción: eliminar puntos finales y espacios extra
            descripcion = descripcion.rstrip(". \t")
            descripcion = re.sub(r"\s+", " ", descripcion)

            # Ignorar si la descripción tiene menos de 3 caracteres (artefacto de parseo)
            if len(descripcion) < 3:
                continue

            # Evitar duplicados (el .md tiene algunos códigos repetidos por error)
            if codigo in seen_codigos:
                print(f"  [DUP] Codigo duplicado ignorado: {codigo} - {descripcion}")
                continue
            seen_codigos.add(codigo)

            nivel = len(codigo)
            elemento = codigo[0]

            records.append({
                "codigo": codigo,
                "descripcion": descripcion,
                "nivel": nivel,
                "elemento": elemento,
            })

    return records


def main() -> int:
    _ensure_import_path()

    from app.brain.db.supabase_client import get_supabase

    md_path = _repo_root() / "plancontable.md"
    if not md_path.exists():
        print(f"ERROR: No se encontró {md_path}")
        return 1

    print(f"Parseando {md_path.name}...")
    records = parse_plan_contable(md_path)
    print(f"Cuentas encontradas: {len(records)}")

    if not records:
        print("No se encontraron cuentas. Revisa el formato del archivo.")
        return 1

    supabase = get_supabase()

    # Insertar en lotes de 200 para evitar timeouts
    BATCH_SIZE = 200
    total_insertados = 0

    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        supabase.table("plan_contable").upsert(batch, on_conflict="codigo").execute()
        total_insertados += len(batch)
        print(f"  Insertados {total_insertados}/{len(records)}...")

    print(f"\nOK Plan Contable cargado exitosamente: {total_insertados} cuentas en Supabase.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
