import csv
import sys
from pathlib import Path

def migrate_clients():
    # Adjust import path
    root = Path(__file__).resolve().parents[3]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from app.brain.db.supabase_client import get_supabase

    csv_path = root / "app" / "clients" / "sunat_clients.csv"
    if not csv_path.exists():
        print(f"No CSV found at {csv_path}")
        return

    supabase = get_supabase()
    
    with csv_path.open("r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None) # skip header if exists
        
        for row in reader:
            if len(row) < 6:
                continue
            name, ruc, username, password, client_id, client_secret = [c.strip() for c in row[:6]]
            
            if not ruc:
                continue
                
            try:
                # Upsert to avoid duplicates
                supabase.table("clientes").upsert({
                    "ruc": ruc,
                    "razon_social": name,
                    "usuario_sol": username,
                    "clave_sol": password,
                    "client_id_api": client_id,
                    "client_secret_api": client_secret,
                    "activo": True
                }, on_conflict="ruc").execute()
                print(f"Migrated client: {name} ({ruc})")
            except Exception as e:
                print(f"Error migrating {ruc}: {e}")

if __name__ == "__main__":
    migrate_clients()
