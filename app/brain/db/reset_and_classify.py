"""
reset_and_classify.py — Migración de datos post-fix del scraper.

Este script clasifica los comprobantes existentes en la base de datos
según lo descubierto en el análisis de 7 clientes:

1. Series físicas/contingentes (FI*, FN*, FQAA, etc.) → NO_DESCARGABLE
2. Tipos aduaneros (50, 52, 53) → NO_DESCARGABLE
3. Electrónicos estándar con reintentos >= 10 → reset a 0 (darles otra oportunidad con código corregido)
"""

import sys
from pathlib import Path

root = Path(__file__).resolve().parents[3]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from app.brain.db.supabase_client import get_supabase


# Series conocidas como fisicas/contingentes que NUNCA tendran XML en SUNAT
SERIES_FISICAS_PREFIXES = ["FI", "FN", "FQAA"]

# Tipos de comprobante que son de aduanas/mensajeria sin XML descargable
TIPOS_NO_DESCARGABLES = ["50", "52", "53"]

# Series electronicas estandar (merecen otra oportunidad)
SERIES_ELECTRONICAS_PREFIXES = ["E", "F0", "FA", "FB", "FC", "FD", "FE", "FF", "B0", "BB", "EB"]


def main():
    sb = get_supabase()
    
    print("=" * 60)
    print("MIGRACION DE DATOS: Clasificacion post-fix del scraper")
    print("=" * 60)
    
    # --- Paso 1: Marcar series fisicas como NO_DESCARGABLE ---
    print("\n[1/3] Buscando comprobantes con series fisicas/contingentes...")
    
    # Obtener todos los PENDIENTE/ERROR
    pending = sb.table("sire_comprobantes_fisicos") \
        .select("id, serie, tipo_cp, reintentos") \
        .or_("estado_xml.in.(PENDIENTE,ERROR),estado_pdf.in.(PENDIENTE,ERROR)") \
        .limit(1000) \
        .execute().data
    
    fisicos_count = 0
    aduanas_count = 0
    reset_count = 0
    
    for r in pending:
        serie = (r["serie"] or "").strip().upper()
        tipo = (r["tipo_cp"] or "").strip()
        
        # Comprobar si es serie fisica
        is_fisico = any(serie.startswith(prefix) for prefix in SERIES_FISICAS_PREFIXES)
        
        # Comprobar si es tipo aduanero
        is_aduanas = tipo in TIPOS_NO_DESCARGABLES
        
        if is_fisico or is_aduanas:
            sb.table("sire_comprobantes_fisicos") \
                .update({
                    "estado_xml": "NO_DESCARGABLE",
                    "estado_pdf": "NO_DESCARGABLE",
                    "error_log": f"Clasificado automaticamente: {'serie fisica/contingente' if is_fisico else 'tipo aduanero/mensajeria'}"
                }) \
                .eq("id", r["id"]) \
                .execute()
            
            if is_fisico:
                fisicos_count += 1
            else:
                aduanas_count += 1
        
        elif r["reintentos"] >= 10:
            # Es electronico estandar pero agoto reintentos -> reset para darle otra oportunidad
            is_electronico = any(serie.startswith(prefix) for prefix in SERIES_ELECTRONICAS_PREFIXES)
            if is_electronico:
                sb.table("sire_comprobantes_fisicos") \
                    .update({
                        "reintentos": 0,
                        "estado_xml": "PENDIENTE",
                        "estado_pdf": "PENDIENTE",
                        "error_log": "Reset post-fix: codigo corregido, segunda oportunidad"
                    }) \
                    .eq("id", r["id"]) \
                    .execute()
                reset_count += 1
            else:
                # Serie desconocida con 10+ reintentos -> NO_EXISTE
                sb.table("sire_comprobantes_fisicos") \
                    .update({
                        "estado_xml": "NO_EXISTE",
                        "estado_pdf": "NO_EXISTE",
                        "error_log": "Agotados 10 reintentos, serie no reconocida como electronica"
                    }) \
                    .eq("id", r["id"]) \
                    .execute()
    
    print(f"   Series fisicas/contingentes -> NO_DESCARGABLE: {fisicos_count}")
    print(f"   Tipos aduaneros/mensajeria  -> NO_DESCARGABLE: {aduanas_count}")
    print(f"   Electronicos estandar       -> reset reintentos: {reset_count}")
    print(f"   Total procesados: {len(pending)}")
    
    # --- Resumen final ---
    print("\n" + "=" * 60)
    print("ESTADO FINAL DE LA BASE DE DATOS:")
    
    for estado in ["PENDIENTE", "DESCARGADO", "NO_DESCARGABLE", "NO_EXISTE", "ERROR"]:
        count_result = sb.table("sire_comprobantes_fisicos") \
            .select("id", count="exact") \
            .eq("estado_xml", estado) \
            .execute()
        print(f"   estado_xml = {estado:15s} : {count_result.count if count_result.count is not None else len(count_result.data)}")
    
    print("=" * 60)
    print("[OK] Migracion completada.")


if __name__ == "__main__":
    main()
