"""
Facturación Electrónica Routes — Quanta

Issues and checks invoices/boletas through the APISUNAT third-party API.
Migrated from the legacy monolithic app/api.py.
"""
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/facturacion", tags=["facturacion"])

APISUNAT_SANDBOX = "https://sandbox.apisunat.pe"
APISUNAT_PROD    = "https://app.apisunat.pe"


class FacturacionEmitirRequest(BaseModel):
    emisor_ruc: str
    receptor: dict
    comprobante: dict
    items: list
    totales: dict
    token: str         # Bearer token del cliente - obtenido en app.apisunat.pe
    sandbox: bool = True  # True = pruebas, False = producción


@router.post("/emitir")
def emitir_comprobante(req: FacturacionEmitirRequest):
    if not req.token:
        raise HTTPException(status_code=400, detail="Se requiere el token de APISUNAT de esta empresa.")

    # Construir el payload que acepta APISUNAT
    # Mapear tipo de comprobante
    tipo_doc_map = {"01": "factura", "03": "boleta"}
    tipo_doc = tipo_doc_map.get(req.comprobante.get("tipo", "01"), "factura")

    # Construir items en formato APISUNAT
    apisunat_items = []
    for item in req.items:
        cantidad = float(item.get("cantidad", 1))
        precio_unitario = float(item.get("precio_unitario", 0))
        # valor_unitario = precio sin IGV
        valor_unitario = precio_unitario / 1.18
        apisunat_items.append({
            "unidad_de_medida": "NIU",
            "descripcion": item.get("descripcion", "Producto"),
            "cantidad": str(cantidad),
            "valor_unitario": f"{valor_unitario:.6f}",
            "porcentaje_igv": "18",
            "codigo_tipo_afectacion_igv": "10",
            "nombre_tributo": "IGV"
        })

    payload = {
        "documento": tipo_doc,
        "serie": req.comprobante.get("serie", "F001"),
        "numero": int(req.comprobante.get("correlativo", 1) or 1),
        "fecha_de_emision": req.comprobante.get("fecha"),
        "moneda": req.comprobante.get("moneda", "PEN"),
        "tipo_operacion": "0101",
        "cliente_tipo_de_documento": "6" if len(req.receptor.get("ruc","")) == 11 else "1",
        "cliente_numero_de_documento": req.receptor.get("ruc", ""),
        "cliente_denominacion": req.receptor.get("razon_social", ""),
        "cliente_direccion": req.receptor.get("direccion", ""),
        "items": apisunat_items,
        "total": f"{req.totales.get('total', 0):.2f}"
    }

    base_url = APISUNAT_SANDBOX if req.sandbox else APISUNAT_PROD
    url = f"{base_url}/api/v3/documents"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {req.token}"
    }

    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=30)
        data = response.json()

        if response.status_code == 200 and data.get("success"):
            payload_resp = data.get("payload", {})
            return {
                "status": "success",
                "estado": payload_resp.get("estado"),
                "message": data.get("message"),
                "xml_url": payload_resp.get("xml"),
                "pdf_url": payload_resp.get("pdf"),
                "cdr_url": payload_resp.get("cdr"),
                "hash": payload_resp.get("hash"),
            }
        else:
            # Devolver el error tal como viene de APISUNAT
            raise HTTPException(
                status_code=response.status_code,
                detail=data.get("message", "Error al emitir en APISUNAT")
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Tiempo de espera agotado conectando con APISUNAT.")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error de conexión con APISUNAT: {str(e)}")


@router.post("/estado")
def consultar_estado(body: dict):
    """Consulta el estado de un comprobante ya emitido en APISUNAT"""
    token = body.get("token", "")
    sandbox = body.get("sandbox", True)
    if not token:
        raise HTTPException(status_code=400, detail="Token requerido")

    base_url = APISUNAT_SANDBOX if sandbox else APISUNAT_PROD
    url = f"{base_url}/api/v3/status"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "serie": body.get("serie"),
        "numero": body.get("numero"),
        "tipo": body.get("tipo", "01"),
        "ruc_emisor": body.get("ruc_emisor")
    }
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=20)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
