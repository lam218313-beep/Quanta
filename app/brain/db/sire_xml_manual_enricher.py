import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[3]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from app.brain.db.supabase_client import get_supabase
from app.brain.sire_xml_matcher import match_xml_descriptions

def enrich_manual_xmls(ruc: str, periodo: str, tipo_libro: str):
    """
    Busca archivos XML/ZIP descargados manualmente en la carpeta downloads/xml/ y los usa
    para enriquecer la base de datos preliminar de SIRE.
    """
    supabase = get_supabase()
    
    r = supabase.table("clientes").select("id, razon_social").eq("ruc", ruc).execute()
    if not r.data:
        print(f"Error: No se encontró cliente con RUC {ruc}")
        return
        
    cliente = r.data[0]
    cliente_id = cliente["id"]
    razon_social = cliente["razon_social"]
    
    base_dir = root / "downloads" / "xml"
    
    target_dir = None
    if base_dir.exists():
        for p in base_dir.iterdir():
            if p.is_dir() and ruc in p.name:
                folder = p / periodo / ("purchases" if tipo_libro == "COMPRAS" else "sales") / "xml"
                if folder.exists():
                    target_dir = folder
                    break
    
    if not target_dir:
        print(f"Error: No se encontró la carpeta de XMLs manuales para RUC {ruc} periodo {periodo}.")
        print(f"Asegúrate de colocar los archivos .zip o .xml en: downloads/xml/[NOMBRE] {ruc}/{periodo}/[purchases|sales]/xml/")
        return
        
    print(f"Escaneando XMLs manuales en {target_dir}...")
    
    xml_map = match_xml_descriptions(target_dir)
    print(f"Se extrajeron descripciones de {len(xml_map)} comprobantes desde los archivos manuales.")
    
    if not xml_map:
        print("No se encontraron comprobantes en los XMLs manuales. Verifica el archivo.")
        return
        
    table_name = "sire_preliminar_compras" if tipo_libro == "COMPRAS" else "sire_preliminar_ventas"
    
    query = supabase.table(table_name) \
        .select("id, nro_doc_identidad, tipo_cp_doc, serie_cdp, nro_cp, estado_enriquecimiento") \
        .eq("cliente_id", cliente_id) \
        .eq("periodo", periodo)
        
    res = query.execute()
    records = res.data
    
    if not records:
        print(f"No hay comprobantes preliminares en {periodo} para enriquecer.")
        return
        
    updated_count = 0
    for r in records:
        try:
            num = str(int(r["nro_cp"])) if r["nro_cp"] else "0"
        except:
            num = str(r["nro_cp"]).lstrip("0") or "0"
            
        if tipo_libro == "VENTAS":
            ruc_match = ruc
        else:
            ruc_match = r["nro_doc_identidad"]

        key = (
            ruc_match,
            r["tipo_cp_doc"],
            r["serie_cdp"],
            num
        )
        
        if key in xml_map:
            info = xml_map[key]
            desc_text = info["descripcion"]
            detraccion = info["detraccion"]
            
            supabase.table(table_name) \
                .update({
                    "descripcion_comprobante": desc_text if desc_text else "Sin descripción",
                    "estado_enriquecimiento": "COMPLETO",
                    "detraccion": detraccion
                }) \
                .eq("id", r["id"]) \
                .execute()
            updated_count += 1
            
    print(f"Enriquecimiento manual completado: {updated_count} comprobantes actualizados en BD.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ruc", type=str, required=True, help="RUC del cliente")
    parser.add_argument("--periodo", type=str, required=True, help="Periodo (ej: 202605)")
    parser.add_argument("--tipo", type=str, required=True, choices=["COMPRAS", "VENTAS"])
    args = parser.parse_args()
    
    enrich_manual_xmls(args.ruc, args.periodo, args.tipo)
