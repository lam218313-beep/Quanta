import pandas as pd
import os
import sys
from pathlib import Path

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]

def _ensure_import_path() -> None:
    root = str(_repo_root())
    if root not in sys.path:
        sys.path.insert(0, root)

def generate_compras_excel(cliente_id: str, periodo: str, output_path: str):
    _ensure_import_path()
    from app.brain.db.supabase_client import get_supabase
    supabase = get_supabase()

    print(f"Buscando compras para cliente {cliente_id} en periodo {periodo}...")
    
    # Obtener todas las compras procesadas
    resp = supabase.table("sire_preliminar_compras") \
        .select("*") \
        .eq("cliente_id", cliente_id) \
        .eq("periodo", periodo) \
        .order("fecha_emision") \
        .execute()
        
    registros = resp.data
    if not registros:
        print("No hay registros para exportar.")
        return False
        
    print(f"Exportando {len(registros)} comprobantes a Excel...")
    
    # Obtener info del cliente para el rubro si se necesita
    cliente_resp = supabase.table("clientes").select("rubro").eq("id", cliente_id).execute()
    rubro_cliente = cliente_resp.data[0]["rubro"] if cliente_resp.data else ""
    
    filas = []
    
    for i, r in enumerate(registros):
        # Mapeo a las 42 columnas (A a AP)
        # Inicializamos todas en None
        fila = [None] * 42
        
        # A: Periodo (e.g. 20260400) - SIRE usa YYYYMM, lo convertimos a YYYYMM00
        fila[0] = f"{r.get('periodo', '')}00" if r.get('periodo') else ""
        
        # B: Voucher Correlativo
        yy = r.get('periodo', '2026')[:4][-2:] # 2026 -> 26
        mm = r.get('periodo', '202604')[-2:]   # 04
        num_voucher = str(i + 1).zfill(4)
        fila[1] = f"{yy}C{mm}{num_voucher}" # ej: 26C040001
        
        # C: Fijo M1
        fila[2] = "M1"
        
        # D: Fecha Emisión (de YYYY-MM-DD a DD/MM/YYYY)
        f_emi = r.get('fecha_emision', '')
        if f_emi and len(f_emi.split('-')) == 3:
            y, m, d = f_emi.split('-')
            fila[3] = f"{d}/{m}/{y}"
            
        # E: Fecha Vencimiento
        f_vcto = r.get('fecha_vcto_pago', '')
        if f_vcto and len(f_vcto.split('-')) == 3:
            y, m, d = f_vcto.split('-')
            fila[4] = f"{d}/{m}/{y}"
            
        # F: Tipo comprobante
        tipo_cp = str(r.get('tipo_cp_doc', ''))
        # Quitar el '0' inicial si es '01' -> '1', '03' -> '3' (según tu Excel)
        fila[5] = int(tipo_cp) if tipo_cp.isdigit() else tipo_cp
        
        # G: Serie
        fila[6] = r.get('serie_cdp', '')
        
        # I: Número
        fila[8] = int(r.get('nro_cp')) if str(r.get('nro_cp', '')).isdigit() else r.get('nro_cp', '')
        
        # K: Tipo Doc Identidad
        tipo_doc = str(r.get('tipo_doc_identidad', ''))
        fila[10] = int(tipo_doc) if tipo_doc.isdigit() else tipo_doc
        
        # L: Nro Doc Identidad
        fila[11] = r.get('nro_doc_identidad', '')
        
        # M: Razón Social
        fila[12] = r.get('razon_social', '')
        
        # N-W: Importes (Base, IGV, Total...)
        fila[13] = r.get('bi_gravado_dg', 0.0)
        fila[14] = r.get('igv_ipm_dg', 0.0)
        fila[15] = r.get('bi_gravado_dgng', 0.0)
        fila[16] = r.get('igv_ipm_dgng', 0.0)
        fila[17] = r.get('bi_gravado_dng', 0.0)
        fila[18] = r.get('igv_ipm_dng', 0.0)
        fila[19] = r.get('valor_adq_ng', 0.0)
        fila[20] = r.get('isc', 0.0)
        fila[21] = r.get('icbper', 0.0)
        fila[22] = r.get('total_cp', 0.0)
        
        # X: Moneda
        fila[23] = r.get('moneda', 'PEN')
        
        # AM (38): Rubro
        fila[38] = rubro_cliente 
        
        # AN (39): Categoria
        fila[39] = r.get('categoria', '')
        
        # AO (40) y AP (41) : Fijos
        fila[40] = 1
        fila[41] = 1
        
        filas.append(fila)
        
    df = pd.DataFrame(filas)
    
    # Guardar en Excel sin cabeceras
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_excel(output_path, index=False, header=False)
    
    print(f"Excel generado exitosamente en: {output_path}")
    return True
