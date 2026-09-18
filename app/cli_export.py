import argparse
import sys
from pathlib import Path

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]

def _ensure_import_path() -> None:
    root = str(_repo_root())
    if root not in sys.path:
        sys.path.insert(0, root)

def main():
    parser = argparse.ArgumentParser(description="Exportador a Matriz de Carga Masiva (Excel)")
    parser.add_argument("--cliente_id", required=True, help="ID del cliente en Supabase")
    parser.add_argument("--periodo", required=True, help="Periodo a exportar (YYYYMM)")
    parser.add_argument("--out", required=False, help="Ruta de salida del Excel", default="downloads/export.xlsx")
    
    args = parser.parse_args()
    
    _ensure_import_path()
    
    from app.brain.db.excel_exporter import generate_compras_excel
    
    # Resolver ruta absoluta para el output
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = _repo_root() / out_path
        
    generate_compras_excel(args.cliente_id, args.periodo, str(out_path))

if __name__ == "__main__":
    main()
