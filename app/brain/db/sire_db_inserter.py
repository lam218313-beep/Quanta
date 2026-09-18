import csv
from pathlib import Path
try:
    from app.brain.db.supabase_client import get_supabase
except ModuleNotFoundError:
    from brain.db.supabase_client import get_supabase


# Prefijos de serie que corresponden a comprobantes electrónicos con XML en SUNAT
_ELECTRONIC_PREFIXES = (
    "F", "B", "E", "EC", "BE", "BD", "FD", "RH", "ER", "FF", "BB", "D",
)

def _is_electronic_serie(serie: str) -> bool:
    """Retorna True si la serie tiene un prefijo de comprobante electrónico.
    Las series sin prefijo (ej. FA01, FQ00, 0001) son documentos físicos
    que usualmente no tienen XML en el portal de SUNAT.
    """
    s = serie.strip().upper()
    if not s:
        return False

    # Prefijo electrónico seguido de dígitos puros: F001, E001, BE01, etc.
    for prefix in sorted(_ELECTRONIC_PREFIXES, key=len, reverse=True):
        if s.startswith(prefix):
            resto = s[len(prefix):]
            if resto.isdigit():          # F001, B001, E001, BE01
                return True
            # Fix C: operadoras grandes (Movistar, Claro, etc.) usan series
            # alfanuméricas como F3M5, F101, FA1A que SÍ son electrónicas
            if resto and resto[0].isdigit():  # empieza con dígito tras prefijo → electrónica
                return True
    return False

def parse_and_insert_sire_txt(client_id: str, periodo: str, book_type: str, txt_path: Path):
    """
    Lee el archivo TXT descargado de SIRE y lo inserta en la base de datos (Bulk Insert).
    También genera las tareas pendientes en sire_comprobantes_fisicos.
    """
    supabase = get_supabase()
    
    # Determinar las tablas según el libro
    is_compras = (book_type == "purchases")
    table_name = "sire_preliminar_compras" if is_compras else "sire_preliminar_ventas"
    tipo_libro = "COMPRAS" if is_compras else "VENTAS"
    
    records = []
    
    with txt_path.open("r", encoding="utf-8") as f:
        # SIRE TXT fields are separated by pipe |
        reader = csv.reader(f, delimiter="|")
        
        # Omitir la primera línea si es cabecera (SIRE suele no tener cabecera en el TXT final, pero la propuesta a veces sí).
        # Verificamos si la primera fila contiene texto de cabecera como "RUC" o "Periodo".
        first_row = next(reader, None)
        if not first_row:
            return
            
        # Omitir filas vacías
        if len(first_row) < 3:
            return
            
        if first_row[0].strip().upper() == "RUC" or first_row[2].strip().upper() == "PERIODO":
            pass # era cabecera
        else:
            # era data, la procesamos
            _process_row(first_row, records, client_id, periodo, is_compras)
            
        for row in reader:
            if not row or len(row) < 10:
                continue
            _process_row(row, records, client_id, periodo, is_compras)
            
    if not records:
        print(f"No hay registros válidos en {txt_path.name} para insertar.")
        return
        
    print(f"Insertando {len(records)} registros en {table_name}...")
    
    # Insertar en BD en lotes de 1000 para evitar saturar
    batch_size = 1000
    inserted_preliminaries = []
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        try:
            # Upsert usando car_sunat como clave única
            response = supabase.table(table_name).upsert(batch, on_conflict="car_sunat").execute()
            inserted_preliminaries.extend(response.data)
        except Exception as e:
            print(f"Error en bulk insert de preliminares: {e}")
            
    # Ahora insertar en la cola de descarga de físicos
    print(f"Insertando {len(inserted_preliminaries)} tareas en sire_comprobantes_fisicos...")
    fisicos_records = []
    
    for p in inserted_preliminaries:
        serie = p.get("serie_cdp", "") or ""
        es_electronico = _is_electronic_serie(serie)

        # Preparamos el registro para sire_comprobantes_fisicos
        r = {
            "cliente_id": client_id,
            "periodo": periodo,
            "tipo_libro": tipo_libro,
            "ruc_tercero": p["nro_doc_identidad"] if is_compras else p["nro_doc_identidad"],
            "tipo_cp": p["tipo_cp_doc"],
            "serie": serie,
            "numero": p["nro_cp"],
            "estado_xml": "PENDIENTE",
            "estado_pdf": "PENDIENTE",
            # Parte B: documentos físicos arrancan con reintentos=9 → solo 1 intento
            # antes de alcanzar el límite de 10 y no volver a entrar en cola.
            "reintentos": 0 if es_electronico else 9,
        }
        
        if is_compras:
            r["preliminar_compra_id"] = p["id"]
        else:
            r["preliminar_venta_id"] = p["id"]
            
        fisicos_records.append(r)
        
    for i in range(0, len(fisicos_records), batch_size):
        batch = fisicos_records[i:i+batch_size]
        try:
            # Usamos índices únicos para evitar duplicados en cola
            supabase.table("sire_comprobantes_fisicos").upsert(
                batch, 
                on_conflict="cliente_id, periodo, tipo_libro, ruc_tercero, tipo_cp, serie, numero"
            ).execute()
        except Exception as e:
            print(f"Error en bulk insert de comprobantes físicos: {e}")
            
    print("Insercion completada con exito.")

def _safe_float(val: str) -> float:
    v = val.strip()
    if not v:
        return 0.0
    try:
        return float(v)
    except:
        return 0.0

def _process_row(row: list, records: list, client_id: str, periodo: str, is_compras: bool):
    # Función auxiliar para mapear las columnas del TXT a nuestro diccionario
    try:
        # Asegurar longitud mínima de columnas llenando con vacíos
        row = row + [""] * (40 - len(row))
        
        if is_compras:
            # Mapeo COMPRAS según el TXT
            record = {
                "cliente_id": client_id,
                "periodo": row[2].strip() or periodo,
                "car_sunat": row[3].strip(),
                "fecha_emision": row[4].strip(),
                "fecha_vcto_pago": row[5].strip() if row[5].strip() else None,
                "tipo_cp_doc": row[6].strip(),
                "serie_cdp": row[7].strip(),
                "nro_cp": row[9].strip(),
                "tipo_doc_identidad": row[11].strip(),
                "nro_doc_identidad": row[12].strip(),
                "razon_social": row[13].strip(),
                "bi_gravado_dg": _safe_float(row[14]),
                "igv_ipm_dg": _safe_float(row[15]),
                "bi_gravado_dgng": _safe_float(row[16]),
                "igv_ipm_dgng": _safe_float(row[17]),
                "bi_gravado_dng": _safe_float(row[18]),
                "igv_ipm_dng": _safe_float(row[19]),
                "valor_adq_ng": _safe_float(row[20]),
                "isc": _safe_float(row[21]),
                "icbper": _safe_float(row[22]),
                "otros_trib_cargos": _safe_float(row[23]),
                "total_cp": _safe_float(row[24]),
                "moneda": row[25].strip(),
                "tipo_cambio": _safe_float(row[26]) if row[26].strip() else 1.000,
                "fecha_doc_mod": row[27].strip() if row[27].strip() else None,
                "tipo_cp_mod": row[28].strip(),
                "serie_cp_mod": row[29].strip(),
                "nro_cp_mod": row[31].strip(),
                "detraccion": row[37].strip(),
            }
        else:
            # Mapeo VENTAS según el TXT
            record = {
                "cliente_id": client_id,
                "periodo": row[2].strip() or periodo,
                "car_sunat": row[3].strip(),
                "fecha_emision": row[4].strip(),
                "fecha_vcto_pago": row[5].strip() if row[5].strip() else None,
                "tipo_cp_doc": row[6].strip(),
                "serie_cdp": row[7].strip(),
                "nro_cp": row[8].strip(), # En ventas, la doc inicial es la col 8 (índice 0-based) o 9?
                # Revisemos el txt de ventas: 0:Ruc, 1:Razon, 2:Periodo, 3:CAR, 4:FechaEm, 5:FechaVcto, 6:Tipo, 7:Serie, 8:NroInicial
                # Sí, índice 8.
                "tipo_doc_identidad": row[10].strip(),
                "nro_doc_identidad": row[11].strip(),
                "razon_social": row[12].strip(),
                "valor_fact_exportacion": _safe_float(row[13]),
                "bi_gravada": _safe_float(row[14]),
                "dscto_bi": _safe_float(row[15]),
                "igv_ipm": _safe_float(row[16]),
                "dscto_igv_ipm": _safe_float(row[17]),
                "mto_exonerado": _safe_float(row[18]),
                "mto_inafecto": _safe_float(row[19]),
                "isc": _safe_float(row[20]),
                "bi_grav_ivap": _safe_float(row[21]),
                "ivap": _safe_float(row[22]),
                "icbper": _safe_float(row[23]),
                "otros_tributos": _safe_float(row[24]),
                "total_cp": _safe_float(row[25]),
                "moneda": row[26].strip(),
                "tipo_cambio": _safe_float(row[27]) if row[27].strip() else 1.000,
                "fecha_doc_mod": row[28].strip() if row[28].strip() else None,
                "tipo_cp_mod": row[29].strip(),
                "serie_cp_mod": row[30].strip(),
                "nro_cp_mod": row[31].strip(),
                "valor_fob_embarcado": _safe_float(row[35]),
            }
            
        # Formatear fechas de DD/MM/YYYY a YYYY-MM-DD
        for f_col in ['fecha_emision', 'fecha_vcto_pago', 'fecha_doc_mod']:
            if record.get(f_col):
                parts = record[f_col].split('/')
                if len(parts) == 3:
                    record[f_col] = f"{parts[2]}-{parts[1]}-{parts[0]}"
                else:
                    record[f_col] = None
                    
        records.append(record)
    except Exception as e:
        print(f"Error mapeando fila: {e}")
