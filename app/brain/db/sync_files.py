import os
import re
from pathlib import Path
from typing import Iterable
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

BASE_DIR = Path(__file__).parent.parent.parent.parent / "downloads"


def _sanitize_folder_name(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


def _candidate_client_dirs(base_xml: Path, ruc_empresa: str, razon_social: str | None) -> list[Path]:
    candidates: list[Path] = []
    if razon_social and ruc_empresa:
        folder_client = f"{_sanitize_folder_name(razon_social)} {ruc_empresa}".strip()
        candidates.append(base_xml / folder_client)

    if ruc_empresa:
        for entry in base_xml.iterdir():
            if entry.is_dir() and ruc_empresa in entry.name:
                candidates.append(entry)

    seen: set[str] = set()
    unique: list[Path] = []
    for p in candidates:
        key = str(p).lower()
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique


def _candidate_dirs_for_period(base_xml: Path, client_dirs: Iterable[Path], periodo: str, book: str) -> list[Path]:
    dirs: list[Path] = []
    for client_dir in client_dirs:
        dirs.extend([
            client_dir / periodo / book / "xml",
            client_dir / periodo / book / "pdf",
            client_dir / periodo / book,
            client_dir / periodo,
        ])

    dirs.extend([
        base_xml / periodo / book,
        base_xml / periodo,
    ])

    seen: set[str] = set()
    unique: list[Path] = []
    for d in dirs:
        key = str(d).lower()
        if key not in seen:
            seen.add(key)
            unique.append(d)
    return unique


def _find_existing_path(base_dirs: Iterable[Path], names: Iterable[str], exts: Iterable[str]) -> Path | None:
    for base_dir in base_dirs:
        if not base_dir.exists():
            continue
        for name in names:
            for ext in exts:
                candidate = base_dir / f"{name}{ext}"
                if candidate.exists():
                    return candidate
    return None

def sync_files():
    print("Iniciando sincronización de archivos físicos con base de datos...")
    
    # Obtener clientes para cruzar IDs
    res = supabase.table("clientes").select("id, ruc, razon_social").execute()
    clientes_map = {c['id']: c for c in res.data}
    
    # Obtener todos los pendientes
    res = supabase.table("sire_comprobantes_fisicos").select(
        "id, cliente_id, periodo, tipo_libro, ruc_tercero, tipo_cp, serie, numero, estado_xml, estado_pdf"
    ).execute()
    print("Escaneando directorio de descargas una sola vez (optimizado)...")
    if BASE_DIR.exists():
        all_files = list(BASE_DIR.rglob("*.*"))
    else:
        all_files = []
        
    file_map = {}
    for f in all_files:
        if f.suffix.lower() in ('.xml', '.pdf', '.zip'):
            file_map[f.name] = str(f)
            
    print(f"Archivos físicos encontrados: {len(file_map)}")
    
    total_sync = 0
    for row in res.data:
        client = clientes_map.get(row['cliente_id'])
        if not client:
            continue

        serie = row['serie']
        numero = row['numero']
        ruc_tercero = row.get('ruc_tercero', '').strip()
        tipo_cp = row.get('tipo_cp', '')
        if not ruc_tercero or ruc_tercero == '-':
            ruc_tercero = client.get('ruc', '')

        filename_base = f"{ruc_tercero}-{tipo_cp}-{serie}-{numero}"
        xml_name = f"{filename_base}.xml"
        zip_name = f"{filename_base}.zip"
        pdf_name = f"{filename_base}.pdf"

        xml_path = file_map.get(xml_name) or file_map.get(zip_name)
        pdf_path = file_map.get(pdf_name)

        updates = {}

        # NOTA: los archivos se suben a Supabase Storage apenas se descargan
        # (sire_bot_orchestrator.py) — esa es la fuente de verdad real, porque
        # el disco local de Railway es efímero y se borra en cada deploy.
        # Este script solo RECUPERA registros que aún no están marcados como
        # descargados pero cuyo archivo sí aparece en el disco de la corrida
        # actual. Nunca revierte un DESCARGADO ya confirmado: que el disco
        # local esté vacío tras un deploy no significa que el archivo se
        # perdió, ya vive en Storage.
        if xml_path and row.get('estado_xml') != 'DESCARGADO':
            updates['ruta_xml'] = xml_path
            updates['estado_xml'] = 'DESCARGADO'

        if pdf_path and row.get('estado_pdf') != 'DESCARGADO':
            updates['ruta_pdf'] = pdf_path
            updates['estado_pdf'] = 'DESCARGADO'

        if updates:
            supabase.table("sire_comprobantes_fisicos").update(updates).eq("id", row["id"]).execute()
            total_sync += 1
            print(f"Sincronizado a descargado: {serie}-{numero}")

    print(f"Sincronización finalizada. {total_sync} archivos enlazados.")

if __name__ == "__main__":
    sync_files()
