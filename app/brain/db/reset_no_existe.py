"""
Script de reset: vuelve a PENDIENTE los registros con estado_xml='NO_EXISTE'
que tienen series electrónicas (F, B, E, BE, BD, FD, RH...).
Estos fallaron por los bugs del dropdown que ya fueron corregidos.

Uso:
    python app/brain/db/reset_no_existe.py
    python app/brain/db/reset_no_existe.py --ruc 20600373065 --periodo 202604
    python app/brain/db/reset_no_existe.py --dry-run   (solo muestra qué resetearía)
"""
import argparse
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[3]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from app.brain.db.supabase_client import get_supabase
from app.brain.db.sire_db_inserter import _is_electronic_serie


def reset_no_existe(ruc: str = None, periodo: str = None, dry_run: bool = False):
    supabase = get_supabase()

    print("Buscando registros NO_EXISTE con series electrónicas...")
    if ruc:
        print(f"  Filtro RUC: {ruc}")
    if periodo:
        print(f"  Filtro Periodo: {periodo}")

    # Resolver cliente_id si se pasó RUC
    cliente_id = None
    if ruc:
        r = supabase.table("clientes").select("id").eq("ruc", ruc).execute()
        if not r.data:
            print(f"Error: No se encontró cliente con RUC {ruc}")
            return
        cliente_id = r.data[0]["id"]

    query = (
        supabase.table("sire_comprobantes_fisicos")
        .select("id, serie, tipo_cp, tipo_libro, reintentos")
        .or_("estado_xml.eq.NO_EXISTE,estado_xml.eq.ERROR,estado_pdf.eq.ERROR")
    )
    if cliente_id:
        query = query.eq("cliente_id", cliente_id)
    if periodo:
        query = query.eq("periodo", periodo)

    resp = query.limit(2000).execute()
    records = resp.data

    if not records:
        print("No hay registros NO_EXISTE para evaluar.")
        return

    print(f"\nTotal a resetear : {len(records)} (se resetean todos a PENDIENTE)")

    if dry_run:
        print("\n[DRY RUN] Ejemplos a resetear:")
        for r in records[:20]:
            print(f"  id={r['id']} | serie={r['serie']} | tipo={r['tipo_cp']} | {r['tipo_libro']}")
        return

    # Resetear en lotes de 500
    ids_to_reset = [r["id"] for r in records]
    batch_size = 500
    reseteados = 0

    for i in range(0, len(ids_to_reset), batch_size):
        batch = ids_to_reset[i : i + batch_size]
        supabase.table("sire_comprobantes_fisicos").update({
            "estado_xml": "PENDIENTE",
            "estado_pdf": "PENDIENTE",
            "reintentos": 0,          # reiniciar contador de intentos
            "error_log": None,
        }).in_("id", batch).execute()
        reseteados += len(batch)
        print(f"  Reseteados: {reseteados}/{len(ids_to_reset)}")

    print(f"\n[OK] Reset completado: {reseteados} registros vuelven a PENDIENTE.")
    print("Ahora ejecuta el orchestrator para reintentar las descargas.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset de registros NO_EXISTE con series electrónicas")
    parser.add_argument("--ruc", type=str, help="RUC del cliente a filtrar")
    parser.add_argument("--periodo", type=str, help="Periodo a filtrar (ej: 202604)")
    parser.add_argument("--dry-run", action="store_true", help="Solo mostrar qué se resetearía sin hacer cambios")
    args = parser.parse_args()

    reset_no_existe(ruc=args.ruc, periodo=args.periodo, dry_run=args.dry_run)
