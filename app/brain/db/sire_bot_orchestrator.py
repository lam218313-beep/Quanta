import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Ensure we can import app modules
root = Path(__file__).resolve().parents[3]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from app.brain.db.supabase_client import get_supabase
from app.brain.download_xml_scraper import CpeQuery, run_batch

STORAGE_BUCKET = "comprobantes-fisicos"


def _upload_to_storage(supabase, local_path: str, cliente_id: str, periodo: str, tipo_libro: str) -> str | None:
    """Sube un XML/PDF recien descargado al bucket persistente y devuelve su ruta en Storage.

    El disco de Railway es efimero y se borra en cada deploy; Storage es la
    fuente de verdad real para estos archivos. Si la subida falla, devuelve
    None y el llamador conserva la ruta local (se perdera en el proximo
    deploy, pero no se pierde el resultado de la corrida de hoy).
    """
    try:
        local = Path(local_path)
        content = local.read_bytes()
        storage_path = f"{cliente_id}/{periodo}/{tipo_libro}/{local.name}"
        suffix = local.suffix.lower()
        content_type = (
            "application/pdf" if suffix == ".pdf"
            else "application/zip" if suffix == ".zip"
            else "application/xml"
        )
        supabase.storage.from_(STORAGE_BUCKET).upload(
            path=storage_path,
            file=content,
            file_options={"content-type": content_type, "upsert": "true"},
        )
        return storage_path
    except Exception as e:
        print(f"   [WARN] No se pudo subir {local_path} a Supabase Storage: {e}")
        return None

async def orchestrate_xml_downloads(limit: int = 50, outdir: str = "downloads/xml", headless: bool = False, ruc: str = None, periodo: str = None, tipo_libro: str = None, skip_pdf: bool = False):
    """
    Busca comprobantes físicos pendientes en la base de datos, extrae la data preliminar
    requerida (monto, fecha) y orquesta la descarga usando el scraper de Playwright.

    skip_pdf: si True, omite la generación automática de PDFs al final (usado por
    daily_sync.py Fase 1, que la corre una sola vez de forma global para todos los
    clientes en su propia Fase 2 en vez de repetirla por cliente). El disparo manual
    desde el frontend ("Descargar Físicos") sigue generando el PDF de inmediato como
    siempre, dejando skip_pdf en False.
    """
    supabase = get_supabase()
    
    print(f"Buscando hasta {limit} comprobantes pendientes de descargar XML...")
    if ruc:
        print(f"  Filtro RUC: {ruc}")
    if periodo:
        print(f"  Filtro Periodo: {periodo}")
    if tipo_libro:
        print(f"  Filtro Tipo Libro: {tipo_libro}")
    
    # Resolve cliente_id from RUC first (more reliable than join filter)
    cliente_id = None
    if ruc:
        r = supabase.table("clientes").select("id").eq("ruc", ruc).execute()
        if not r.data:
            print(f"Error: No se encontró cliente con RUC {ruc}")
            return
        cliente_id = r.data[0]["id"]
    
    query = supabase.table("sire_comprobantes_fisicos") \
        .select(
            "id, cliente_id, periodo, tipo_libro, ruc_tercero, tipo_cp, serie, numero, reintentos, "
            "sire_preliminar_compras(fecha_emision, total_cp, car_sunat), "
            "sire_preliminar_ventas(fecha_emision, total_cp, car_sunat), "
            "clientes!inner(ruc, razon_social)"
        ) \
        .or_("estado_xml.in.(PENDIENTE,ERROR),estado_pdf.in.(PENDIENTE,ERROR)") \
        .lt("reintentos", 10)
        
    if cliente_id:
        query = query.eq("cliente_id", cliente_id)
    
    if periodo:
        query = query.eq("periodo", periodo)
        
    if tipo_libro:
        query = query.eq("tipo_libro", tipo_libro)
        
    response = query.limit(limit).execute()
        
    records = response.data
    if not records:
        print("No hay comprobantes pendientes por descargar.")
    
    # --- Fase 3B: Transicionar comprobantes con reintentos agotados a NO_EXISTE ---
    stale_query = supabase.table("sire_comprobantes_fisicos") \
        .select("id") \
        .or_("estado_xml.in.(PENDIENTE,ERROR),estado_pdf.in.(PENDIENTE,ERROR)") \
        .gte("reintentos", 10)
    
    if cliente_id:
        stale_query = stale_query.eq("cliente_id", cliente_id)
    if periodo:
        stale_query = stale_query.eq("periodo", periodo)
    if tipo_libro:
        stale_query = stale_query.eq("tipo_libro", tipo_libro)
    
    stale_records = stale_query.limit(200).execute().data
    if stale_records:
        print(f"   [cementerio] {len(stale_records)} comprobantes alcanzaron 10 reintentos -> NO_EXISTE")
        for sr in stale_records:
            supabase.table("sire_comprobantes_fisicos") \
                .update({
                    "estado_xml": "NO_EXISTE",
                    "estado_pdf": "NO_EXISTE",
                    "error_log": "Agotados 10 reintentos sin exito"
                }) \
                .eq("id", sr["id"]) \
                .execute()
    
    if not records:
        return
        
    print(f"Encontrados {len(records)} comprobantes en cola. Preparando queries...")
    
    queries: List[CpeQuery] = []
    record_map: Dict[str, dict] = {}  # key principal: period-ruc-tipo-serie-numero
    record_map_notipo: Dict[str, dict] = {}  # key secundaria: period-ruc-serie-numero (sin tipo)
    
    for r in records:
        is_compra = (r["tipo_libro"] == "COMPRAS")
        preliminar = r["sire_preliminar_compras"] if is_compra else r["sire_preliminar_ventas"]
        
        if not preliminar:
            print(f"Registro {r['id']} no tiene data preliminar asociada. Saltando.")
            continue
            
        # Formatear fecha para el scraper (dd/mm/yyyy)
        fecha_db = preliminar.get("fecha_emision", "")
        fecha_scraper = ""
        if fecha_db:
            parts = fecha_db.split("-")
            if len(parts) == 3:
                fecha_scraper = f"{parts[2]}/{parts[1]}/{parts[0]}"
                
        # Get ruc_cliente
        ruc_cliente = r["clientes"]["ruc"] if r.get("clientes") else ""
        razon_social = r["clientes"]["razon_social"] if r.get("clientes") else ""
        
        q = CpeQuery(
            ruc_emisor=r["ruc_tercero"],
            tipo=r["tipo_cp"],
            serie=r["serie"],
            numero=r["numero"],
            importe=str(preliminar.get("total_cp", "")),
            fecha=fecha_scraper,
            period=r["periodo"],
            book="purchases" if is_compra else "sales",
            car_sunat=preliminar.get("car_sunat", ""),
            ruc_cliente=ruc_cliente,
            razon_social_cliente=razon_social
        )
        queries.append(q)
        
        # Clave principal (con tipo) — usada cuando el tipo coincide exactamente
        key = f"{q.period}-{q.ruc_emisor}-{q.tipo}-{q.serie}-{q.numero}"
        record_map[key] = r
        # Clave secundaria (sin tipo) — usada cuando el scraper encontró el doc con un tipo alternativo (fallback)
        key_notipo = f"{q.period}-{q.ruc_emisor}-{q.serie}-{q.numero}"
        record_map_notipo[key_notipo] = r
        
        # Increment intentos
        supabase.table("sire_comprobantes_fisicos") \
            .update({"reintentos": r["reintentos"] + 1}) \
            .eq("id", r["id"]) \
            .execute()
            
    if not queries:
        return
        
    print("Iniciando Playwright scraper...")
    try:
        results = await run_batch(
            queries,
            outdir=str(Path(root) / outdir),
            prefer="either",
            headless=headless,
            skip_existing=True,  # ESTO ES VITAL: Si el archivo ya existe localmente, lo salta al instante en vez de intentar descargarlo de nuevo
            limit=limit
        )
        
        print("\nProcesando resultados y actualizando la base de datos...")
        for res in results:
            key = f"{res['period']}-{res['ruc_emisor']}-{res['tipo']}-{res['serie']}-{res['numero']}"
            db_record = record_map.get(key)
            if not db_record:
                # Fallback: el scraper usó un tipo alternativo; buscar ignorando el tipo
                key_notipo = f"{res['period']}-{res['ruc_emisor']}-{res['serie']}-{res['numero']}"
                db_record = record_map_notipo.get(key_notipo)
                if db_record:
                    print(f"   [fallback-match] Registro encontrado por clave sin tipo: {key_notipo}")
            if not db_record:
                print(f"   [WARN] No se encontró registro DB para resultado: {key}")
                continue
                
            status = res.get("status")
            ruta = res.get("path", "")
            
            update_data = {}
            if status in ("ok", "skipped"):
                paths = res.get("paths", [])
                for ruta in paths:
                    ruta_lower = ruta.lower()
                    if ruta_lower.endswith(".pdf"):
                        is_pdf = True
                    elif ruta_lower.endswith(".xml") or ruta_lower.endswith(".zip"):
                        is_pdf = False
                    else:
                        is_pdf = "/pdf/" in ruta.replace("\\", "/") or "\\pdf\\" in ruta

                    stored_path = _upload_to_storage(
                        supabase, ruta, db_record["cliente_id"], db_record["periodo"], db_record["tipo_libro"]
                    ) or ruta

                    if is_pdf:
                        update_data["estado_pdf"] = "DESCARGADO"
                        update_data["ruta_pdf"] = stored_path
                    else:
                        update_data["estado_xml"] = "DESCARGADO"
                        update_data["ruta_xml"] = stored_path

            elif status == "not_found":
                # El comprobante no aparece en SUNAT en absoluto
                update_data["estado_xml"] = "PENDIENTE"
                update_data["error_log"] = "No encontrado en SUNAT"
            elif status == "no_descargable":
                # El comprobante EXISTE en SUNAT pero no tiene boton XML/PDF
                # Estado terminal: no reintentar jamas
                update_data["estado_xml"] = "NO_DESCARGABLE"
                update_data["estado_pdf"] = "NO_DESCARGABLE"
                update_data["error_log"] = "Comprobante existe en SUNAT pero sin boton de descarga (fisico/contingente/aduanas)"
            else:
                update_data["estado_xml"] = "PENDIENTE"
                update_data["error_log"] = res.get("error", "Error desconocido")
                
            supabase.table("sire_comprobantes_fisicos") \
                .update(update_data) \
                .eq("id", db_record["id"]) \
                .execute()
                
        print("Base de datos de comprobantes fisicos actualizada.")
        
        # AUTO-SYNC: Re-scan disco y actualizar estados DESCARGADO en la BD
        # Esto garantiza que el frontend siempre muestre el estado real.
        print("\nSincronizando archivos fisicos con base de datos...")
        try:
            from app.brain.db.sync_files import sync_files
            sync_files()
        except Exception as sync_err:
            print(f"Advertencia: sync_files falló: {sync_err}")
        
        # AUTO-GENERATE PDFs: Generar PDFs desde los XMLs recién descargados
        # Esto reemplaza la descarga lenta de PDFs desde el portal de SUNAT.
        if skip_pdf:
            print("\n[skip-pdf] Generación de PDFs omitida (se hará globalmente más adelante).")
        else:
            print("\nGenerando PDFs desde XMLs descargados...")
            try:
                from app.brain.services.pdf_from_xml_service import generate_pdfs_from_xmls
                pdf_result = await generate_pdfs_from_xmls(
                    ruc=ruc,
                    periodo=periodo,
                    tipo_libro=tipo_libro,
                    limit=limit,
                )
                print(f"PDFs generados: {pdf_result.get('generated', 0)}, Errores: {pdf_result.get('errors', 0)}")
            except Exception as pdf_err:
                print(f"Advertencia: generación de PDFs falló: {pdf_err}")
        
    except Exception as e:
        print(f"Error catastrófico en la orquestación: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--ruc", type=str, help="RUC de la empresa para filtrar")
    parser.add_argument("--periodo", type=str, help="Periodo a descargar (ej: 202604)")
    parser.add_argument("--tipo_libro", type=str, help="Tipo de libro a filtrar (COMPRAS o VENTAS)")
    parser.add_argument("--skip-pdf", action="store_true", help="Omitir la generación automática de PDFs al final")
    args = parser.parse_args()

    asyncio.run(orchestrate_xml_downloads(limit=args.limit, headless=args.headless, ruc=args.ruc, periodo=args.periodo, tipo_libro=args.tipo_libro, skip_pdf=args.skip_pdf))
