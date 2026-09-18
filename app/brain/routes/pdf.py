from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
from typing import Optional

from app.brain.pdf_generator import generate_invoice_pdf_from_xml, generate_client_report_pdf
from app.brain.db.supabase_client import get_supabase

router = APIRouter(prefix="/api/pdf", tags=["pdf"])

TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads", "tmp_pdf")
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/invoice")
async def generate_invoice_pdf(file: UploadFile = File(...)):
    """Generate a PDF from an uploaded SUNAT XML file."""
    if file.content_type not in ["text/xml", "application/xml"]:
        raise HTTPException(400, "File must be an XML")
        
    xml_content = await file.read()
    output_filename = f"invoice_{uuid.uuid4().hex}.pdf"
    output_path = os.path.join(TEMP_DIR, output_filename)
    
    try:
        await generate_invoice_pdf_from_xml(xml_content, output_path)
        return FileResponse(path=output_path, filename="factura.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(500, f"Error generating PDF: {str(e)}")

class ReportRequest(BaseModel):
    cliente_id: str
    periodo: str

@router.post("/report")
async def generate_report_pdf(req: ReportRequest):
    """Generate a financial report PDF for a given client and period."""
    supabase = get_supabase()
    
    # Get client info
    c_res = supabase.table("clientes").select("*").eq("id", req.cliente_id).execute()
    if not c_res.data:
        raise HTTPException(404, "Client not found")
    cliente = c_res.data[0]
    
    # Get financial info from sire_comprobantes_fisicos for the given period
    # To keep it simple, we just aggregate the totals
    comp_res = supabase.table("sire_comprobantes_fisicos").select("*, sire_preliminar_compras(*), sire_preliminar_ventas(*)").eq("cliente_id", req.cliente_id).eq("periodo", req.periodo).execute()
    
    ventas = compras = igv_ventas = igv_compras = ventas_base = compras_base = 0.0
    docs_ventas = docs_compras = 0
    
    for r in comp_res.data:
        is_compra = r.get("tipo_libro") == "COMPRAS"
        preliminar = r.get("sire_preliminar_compras") if is_compra else r.get("sire_preliminar_ventas")
        
        total = 0.0
        # preliminar podria ser un dict (si se unió) o None
        if isinstance(preliminar, list) and len(preliminar) > 0:
            preliminar = preliminar[0]
            
        if preliminar and isinstance(preliminar, dict) and "total_cp" in preliminar:
            try:
                total = float(preliminar["total_cp"])
            except:
                pass
        
        # Approximate Base and IGV (Assuming 18%)
        base = total / 1.18
        igv = total - base
        
        if is_compra:
            docs_compras += 1
            compras += total
            compras_base += base
            igv_compras += igv
        else:
            docs_ventas += 1
            ventas += total
            ventas_base += base
            igv_ventas += igv
            
    report_data = {
        "cliente": {"ruc": cliente.get("ruc", "000"), "razon_social": cliente.get("razon_social", "Desconocido")},
        "periodo": req.periodo,
        "resumen": {
            "ventas": ventas,
            "compras": compras,
            "igv_ventas": igv_ventas,
            "igv_compras": igv_compras,
            "ventas_base": ventas_base,
            "compras_base": compras_base,
            "docs_ventas": docs_ventas,
            "docs_compras": docs_compras
        }
    }
    
    output_filename = f"report_{req.cliente_id}_{req.periodo}.pdf"
    output_path = os.path.join(TEMP_DIR, output_filename)
    
    try:
        await generate_client_report_pdf(report_data, output_path)
        return FileResponse(path=output_path, filename=f"Reporte_{req.periodo}.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(500, f"Error generating Report: {str(e)}")
