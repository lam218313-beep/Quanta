import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_root))

from app.brain.db.supabase_client import get_supabase
from app.brain.services.pdf_from_xml_service import _batch_html_to_pdf
from app.brain.pdf_generator import parse_sunat_xml, env as jinja_env
from playwright.async_api import async_playwright

async def main():
    supabase = get_supabase()
    print("Buscando facturas pendientes de PDF...")
    
    # Get 5 pending XMLs
    res = supabase.table("sire_comprobantes_fisicos").select("*").eq("estado_xml", "DESCARGADO").eq("estado_pdf", "PENDIENTE").limit(5).execute()
    
    records = res.data
    if not records:
        print("No hay facturas con XML descargado y PDF pendiente para probar.")
        return

    output_dir = _root / "scratch" / "pdfs_prueba"
    os.makedirs(output_dir, exist_ok=True)
    
    template = jinja_env.get_template("invoice_template.html")
    jobs = []
    
    print(f"Encontradas {len(records)} facturas. Generando PDFs en {output_dir} ...")
    
    for row in records:
        xml_path = row.get("ruta_xml")
        if not xml_path:
            continue
            
        if xml_path.startswith("/app/"):
            xml_path = xml_path[5:]
        full_xml_path = _root / xml_path.lstrip("/")
        if not full_xml_path.exists():
            print(f"Archivo XML no encontrado: {full_xml_path}")
            continue
            
        with open(full_xml_path, "rb") as f:
            xml_bytes = f.read()
            
        import zipfile
        import io
        if xml_bytes.startswith(b"PK"):
            try:
                with zipfile.ZipFile(io.BytesIO(xml_bytes)) as z:
                    xml_filename = next(name for name in z.namelist() if name.lower().endswith('.xml'))
                    xml_bytes = z.read(xml_filename)
            except Exception as e:
                print(f"Error unzipping file {full_xml_path}: {e}")
                continue
            
        # Parse XML
        data = parse_sunat_xml(xml_bytes)
        if not data:
            print(f"Error parseando XML: {full_xml_path}")
            continue
            
        # Render HTML
        html_content = template.render(data=data)
        
        # Output path
        nro_doc = row.get('nro_cp', 'COMPROBANTE')
        pdf_name = f"{row.get('tipo_cp_doc')}-{nro_doc}.pdf"
        output_pdf_path = str(output_dir / pdf_name)
        
        jobs.append((html_content, output_pdf_path))
    
    if jobs:
        print("Iniciando Playwright para renderizar...")
        results = await _batch_html_to_pdf(jobs, concurrency=1)
        for path, err in results.items():
            if err:
                print(f"Error generando {path}: {err}")
            else:
                print(f"PDF generado exitosamente: {path}")
    
    print("\n¡Proceso de prueba completado sin alterar la base de datos!")

if __name__ == "__main__":
    asyncio.run(main())
