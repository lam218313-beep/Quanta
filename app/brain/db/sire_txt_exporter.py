from typing import List, Dict

def _format_date(iso_date: str) -> str:
    """Convierte YYYY-MM-DD a DD/MM/YYYY. Retorna '' si es nulo."""
    if not iso_date:
        return ""
    parts = iso_date.split("-")
    if len(parts) == 3:
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    return iso_date

def _format_num(num) -> str:
    """Retorna número a 2 decimales sin comas, o '' si es nulo/cero."""
    if num is None or num == "":
        return ""
    try:
        val = float(num)
        if val == 0:
            return "0.00"
        return f"{val:.2f}"
    except:
        return ""

def _format_tipo_cambio(num) -> str:
    """Tipo de cambio a 3 decimales."""
    if num is None or num == "":
        return ""
    try:
        val = float(num)
        return f"{val:.3f}"
    except:
        return ""

def build_sire_compras_txt(records: List[Dict], ruc: str, periodo: str) -> str:
    """
    Reconstruye el TXT de Compras (Anexo 8) con ~43 columnas.
    """
    lines = []
    for r in records:
        row = [""] * 43
        row[0] = ruc
        row[1] = "" # Razon social emisor del txt (puede ir vacío)
        row[2] = r.get("periodo") or periodo
        row[3] = r.get("car_sunat") or ""
        row[4] = _format_date(r.get("fecha_emision"))
        row[5] = _format_date(r.get("fecha_vcto_pago"))
        row[6] = r.get("tipo_cp_doc") or ""
        row[7] = r.get("serie_cdp") or ""
        row[8] = "" # DUA/DSI
        row[9] = r.get("nro_cp") or ""
        row[10] = ""
        row[11] = r.get("tipo_doc_identidad") or ""
        row[12] = r.get("nro_doc_identidad") or ""
        row[13] = r.get("razon_social") or ""
        row[14] = _format_num(r.get("bi_gravado_dg"))
        row[15] = _format_num(r.get("igv_ipm_dg"))
        row[16] = _format_num(r.get("bi_gravado_dgng"))
        row[17] = _format_num(r.get("igv_ipm_dgng"))
        row[18] = _format_num(r.get("bi_gravado_dng"))
        row[19] = _format_num(r.get("igv_ipm_dng"))
        row[20] = _format_num(r.get("valor_adq_ng"))
        row[21] = _format_num(r.get("isc"))
        row[22] = _format_num(r.get("icbper"))
        row[23] = _format_num(r.get("otros_trib_cargos"))
        row[24] = _format_num(r.get("total_cp"))
        row[25] = r.get("moneda") or ""
        row[26] = _format_tipo_cambio(r.get("tipo_cambio"))
        row[27] = _format_date(r.get("fecha_doc_mod"))
        row[28] = r.get("tipo_cp_mod") or ""
        row[29] = r.get("serie_cp_mod") or ""
        row[30] = "" # DUA mod
        row[31] = r.get("nro_cp_mod") or ""
        
        # Unir con plecas y añadir pleca al final
        lines.append("|".join(row) + "|")
        
    return "\n".join(lines)

def build_sire_ventas_txt(records: List[Dict], ruc: str, periodo: str) -> str:
    """
    Reconstruye el TXT de Ventas (Anexo 11) con ~40 columnas.
    """
    lines = []
    for r in records:
        row = [""] * 40
        row[0] = ruc
        row[1] = "" # Razon social
        row[2] = r.get("periodo") or periodo
        row[3] = r.get("car_sunat") or ""
        row[4] = _format_date(r.get("fecha_emision"))
        row[5] = _format_date(r.get("fecha_vcto_pago"))
        row[6] = r.get("tipo_cp_doc") or ""
        row[7] = r.get("serie_cdp") or ""
        row[8] = r.get("nro_cp") or ""
        row[9] = "" # Nro final
        row[10] = r.get("tipo_doc_identidad") or ""
        row[11] = r.get("nro_doc_identidad") or ""
        row[12] = r.get("razon_social") or ""
        row[13] = _format_num(r.get("valor_fact_exportacion"))
        row[14] = _format_num(r.get("bi_gravada"))
        row[15] = _format_num(r.get("dscto_bi"))
        row[16] = _format_num(r.get("igv_ipm"))
        row[17] = _format_num(r.get("dscto_igv_ipm"))
        row[18] = _format_num(r.get("mto_exonerado"))
        row[19] = _format_num(r.get("mto_inafecto"))
        row[20] = _format_num(r.get("isc"))
        row[21] = _format_num(r.get("bi_grav_ivap"))
        row[22] = _format_num(r.get("ivap"))
        row[23] = _format_num(r.get("icbper"))
        row[24] = _format_num(r.get("otros_tributos"))
        row[25] = _format_num(r.get("total_cp"))
        row[26] = r.get("moneda") or ""
        row[27] = _format_tipo_cambio(r.get("tipo_cambio"))
        row[28] = _format_date(r.get("fecha_doc_mod"))
        row[29] = r.get("tipo_cp_mod") or ""
        row[30] = r.get("serie_cp_mod") or ""
        row[31] = r.get("nro_cp_mod") or ""
        row[35] = _format_num(r.get("valor_fob_embarcado"))
        
        # Unir con plecas y añadir pleca al final
        lines.append("|".join(row) + "|")
        
    return "\n".join(lines)

def build_custom_compras_txt(records: List[Dict], ruc: str, periodo: str) -> str:
    """
    Exporta el TXT de Compras en formato personalizado para el sistema contable (M1).
    Reemplaza las primeras 4 columnas de SIRE con Periodo00, CUO, M1.
    """
    lines = []
    for idx, r in enumerate(records, start=1):
        row = [""] * 43
        p = r.get("periodo") or periodo
        
        # Nuevas 3 columnas
        row[0] = f"{p}00"
        year_short = p[2:4] if len(p) >= 4 else "00"
        month = p[4:6] if len(p) >= 6 else "00"
        row[1] = f"{year_short}C{month}{idx:04d}"
        row[2] = "M1"
        
        # A partir de aqu, mantenemos las columnas SIRE (desplazadas -1 porque 4 se vuelven 3)
        row[3] = _format_date(r.get("fecha_emision"))
        row[4] = _format_date(r.get("fecha_vcto_pago"))
        row[5] = r.get("tipo_cp_doc") or ""
        row[6] = r.get("serie_cdp") or ""
        row[7] = "" # DUA/DSI
        row[8] = r.get("nro_cp") or ""
        row[9] = ""
        row[10] = r.get("tipo_doc_identidad") or ""
        row[11] = r.get("nro_doc_identidad") or ""
        row[12] = r.get("razon_social") or ""
        row[13] = _format_num(r.get("bi_gravado_dg"))
        row[14] = _format_num(r.get("igv_ipm_dg"))
        row[15] = _format_num(r.get("bi_gravado_dgng"))
        row[16] = _format_num(r.get("igv_ipm_dgng"))
        row[17] = _format_num(r.get("bi_gravado_dng"))
        row[18] = _format_num(r.get("igv_ipm_dng"))
        row[19] = _format_num(r.get("valor_adq_ng"))
        row[20] = _format_num(r.get("isc"))
        row[21] = _format_num(r.get("icbper"))
        row[22] = _format_num(r.get("otros_trib_cargos"))
        row[23] = _format_num(r.get("total_cp"))
        row[24] = r.get("moneda") or ""
        row[25] = _format_tipo_cambio(r.get("tipo_cambio"))
        row[26] = _format_date(r.get("fecha_doc_mod"))
        row[27] = r.get("tipo_cp_mod") or ""
        row[28] = r.get("serie_cp_mod") or ""
        row[29] = "" # DUA mod
        row[30] = r.get("nro_cp_mod") or ""
        
        # Eliminar el ltimo elemento vaco ya que ahora son 42 columnas en lugar de 43
        row = row[:-1]
        lines.append("|".join(row) + "|")
        
    return "\n".join(lines)

def build_custom_ventas_txt(records: List[Dict], ruc: str, periodo: str) -> str:
    """
    Exporta el TXT de Ventas en formato personalizado para el sistema contable (M1).
    Reemplaza las primeras 4 columnas de SIRE con Periodo00, CUO, M1.
    """
    lines = []
    for idx, r in enumerate(records, start=1):
        row = [""] * 40
        p = r.get("periodo") or periodo
        
        # Nuevas 3 columnas
        row[0] = f"{p}00"
        year_short = p[2:4] if len(p) >= 4 else "00"
        month = p[4:6] if len(p) >= 6 else "00"
        row[1] = f"{year_short}V{month}{idx:04d}"
        row[2] = "M1"
        
        # A partir de aqu, mantenemos las columnas SIRE
        row[3] = _format_date(r.get("fecha_emision"))
        row[4] = _format_date(r.get("fecha_vcto_pago"))
        row[5] = r.get("tipo_cp_doc") or ""
        row[6] = r.get("serie_cdp") or ""
        row[7] = r.get("nro_cp") or ""
        row[8] = "" # Nro final
        row[9] = r.get("tipo_doc_identidad") or ""
        row[10] = r.get("nro_doc_identidad") or ""
        row[11] = r.get("razon_social") or ""
        row[12] = _format_num(r.get("valor_fact_exportacion"))
        row[13] = _format_num(r.get("bi_gravada"))
        row[14] = _format_num(r.get("dscto_bi"))
        row[15] = _format_num(r.get("igv_ipm"))
        row[16] = _format_num(r.get("dscto_igv_ipm"))
        row[17] = _format_num(r.get("mto_exonerado"))
        row[18] = _format_num(r.get("mto_inafecto"))
        row[19] = _format_num(r.get("isc"))
        row[20] = _format_num(r.get("bi_grav_ivap"))
        row[21] = _format_num(r.get("ivap"))
        row[22] = _format_num(r.get("icbper"))
        row[23] = _format_num(r.get("otros_tributos"))
        row[24] = _format_num(r.get("total_cp"))
        row[25] = r.get("moneda") or ""
        row[26] = _format_tipo_cambio(r.get("tipo_cambio"))
        row[27] = _format_date(r.get("fecha_doc_mod"))
        row[28] = r.get("tipo_cp_mod") or ""
        row[29] = r.get("serie_cp_mod") or ""
        row[30] = r.get("nro_cp_mod") or ""
        row[34] = _format_num(r.get("valor_fob_embarcado"))
        
        row = row[:-1]
        lines.append("|".join(row) + "|")
        
    return "\n".join(lines)
