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
    total_reverted = 0
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
        
        # Sincronización XML/ZIP
        if xml_path:
            if row.get('ruta_xml') != xml_path or row.get('estado_xml') != 'DESCARGADO':
                updates['ruta_xml'] = xml_path
                updates['estado_xml'] = 'DESCARGADO'
        elif row.get('estado_xml') == 'DESCARGADO':
            updates['ruta_xml'] = None
            updates['estado_xml'] = 'PENDIENTE'
            updates['reintentos'] = 0
            
        # Sincronización PDF
        if pdf_path:
            if row.get('ruta_pdf') != pdf_path or row.get('estado_pdf') != 'DESCARGADO':
                updates['ruta_pdf'] = pdf_path
                updates['estado_pdf'] = 'DESCARGADO'
        elif row.get('estado_pdf') == 'DESCARGADO':
            updates['ruta_pdf'] = None
            updates['estado_pdf'] = 'PENDIENTE'
            if 'reintentos' not in updates:
                updates['reintentos'] = 0
                
        if updates:
            supabase.table("sire_comprobantes_fisicos").update(updates).eq("id", row["id"]).execute()
            if updates.get('estado_xml') == 'PENDIENTE' or updates.get('estado_pdf') == 'PENDIENTE':
                total_reverted += 1
                print(f"Revertido a pendiente (Archivo faltante): {serie}-{numero}")
            else:
                total_sync += 1
                print(f"Sincronizado a descargado: {serie}-{numero}")
            
    print(f"Sincronización finalizada. {total_sync} archivos enlazados, {total_reverted} revertidos a pendientes.")

if __name__ == "__main__":
    sync_files()
