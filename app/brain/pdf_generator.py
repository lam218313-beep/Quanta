import os
import asyncio
import base64
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
from lxml import etree

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

_LOGO_PATH = os.path.join(TEMPLATE_DIR, "assets", "logo-quanta.png")
_logo_base64_cache = None


def _get_logo_base64() -> str:
    """Read+cache the Quanta logo as base64 so it embeds directly in the PDF HTML."""
    global _logo_base64_cache
    if _logo_base64_cache is None:
        with open(_LOGO_PATH, "rb") as f:
            _logo_base64_cache = base64.b64encode(f.read()).decode("ascii")
    return _logo_base64_cache

async def _html_to_pdf(
    html_content: str,
    output_path: str,
    format_type: str = 'A4',
    header_template: str = None,
    footer_template: str = None,
):
    """
    Convierte HTML a PDF usando Playwright. When header_template/footer_template
    are given, they repeat on every page (Playwright's print header/footer,
    independent of the main content flow) — used for the running report
    header and standard page-numbering footer.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Set HTML content and wait for network/fonts to load
        await page.set_content(html_content, wait_until="networkidle")

        has_header_footer = bool(header_template or footer_template)
        pdf_kwargs = dict(
            path=output_path,
            format=format_type,
            print_background=True,
            display_header_footer=has_header_footer,
        )
        if has_header_footer:
            pdf_kwargs["header_template"] = header_template or "<span></span>"
            pdf_kwargs["footer_template"] = footer_template or "<span></span>"
            pdf_kwargs["margin"] = {"top": "80px", "right": "0", "bottom": "50px", "left": "0"}
        else:
            pdf_kwargs["margin"] = {"top": "0", "right": "0", "bottom": "0", "left": "0"}

        await page.pdf(**pdf_kwargs)
        await browser.close()

def parse_sunat_xml(xml_bytes: bytes) -> Dict[str, Any]:
    """Parse a UBL 2.1 SUNAT XML to extract invoice data."""
    try:
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(xml_bytes, parser=parser)
        
        ns = {"cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
              "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"}
              
        def get(path):
            el = root.find(path, ns)
            return el.text if el is not None else ""
            
        def get_attr(path, attr):
            el = root.find(path, ns)
            return el.get(attr) if el is not None else ""

        # Extract Emisor
        emisor_ruc = get(".//cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID")
        emisor_razon = get(".//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name") or get(".//cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName")
        
        em_dir = root.find(".//cac:AccountingSupplierParty/cac:Party/cac:PostalAddress", ns)
        if em_dir is not None:
            street = em_dir.find("cbc:StreetName", ns)
            dist = em_dir.find("cbc:District", ns)
            city = em_dir.find("cbc:CityName", ns)
            dept = em_dir.find("cbc:CountrySubentity", ns)
            direccion_emisor = f"{street.text if street is not None else ''} {dist.text if dist is not None else ''} - {city.text if city is not None else ''} - {dept.text if dept is not None else ''}".strip(' -')
        else:
            direccion_emisor = ""
        
        # Extract Receptor
        receptor_ruc = get(".//cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID")
        receptor_razon = get(".//cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName")
        
        rec_dir = root.find(".//cac:AccountingCustomerParty/cac:Party/cac:PostalAddress", ns)
        if rec_dir is not None:
            street = rec_dir.find("cbc:StreetName", ns)
            dist = rec_dir.find("cbc:District", ns)
            city = rec_dir.find("cbc:CityName", ns)
            dept = rec_dir.find("cbc:CountrySubentity", ns)
            direccion_receptor = f"{street.text if street is not None else ''} {dist.text if dist is not None else ''} - {city.text if city is not None else ''} - {dept.text if dept is not None else ''}".strip(' -')
        else:
            direccion_receptor = ""

        # Comprobante
        tipo_doc = get(".//cbc:InvoiceTypeCode")
        tipo_str = "FACTURA ELECTRÓNICA" if tipo_doc == "01" else "BOLETA ELECTRÓNICA" if tipo_doc == "03" else "COMPROBANTE ELECTRÓNICO"
        id_doc = get(".//cbc:ID")
        serie = id_doc.split("-")[0] if id_doc and "-" in id_doc else ""
        numero = id_doc.split("-")[1] if id_doc and "-" in id_doc else id_doc
        
        # Format date from YYYY-MM-DD to DD/MM/YYYY
        fecha_raw = get(".//cbc:IssueDate")
        if fecha_raw and "-" in fecha_raw:
            parts = fecha_raw.split("-")
            if len(parts) == 3:
                fecha = f"{parts[2]}/{parts[1]}/{parts[0]}"
            else:
                fecha = fecha_raw
        else:
            fecha = fecha_raw

        moneda_code = get(".//cbc:DocumentCurrencyCode")
        moneda = "SOL" if moneda_code == "PEN" else "DÓLAR ESTADOUNIDENSE" if moneda_code == "USD" else moneda_code
        moneda_simbolo = "S/" if moneda_code == "PEN" else "$" if moneda_code == "USD" else moneda_code

        # Forma de pago (usually Contado or Credito)
        forma_pago = "Contado"
        pt = get(".//cac:PaymentTerms/cbc:ID")
        if pt and "Credito" in pt:
            forma_pago = "Crédito"
            
        # Importe en letras
        importe_letras = ""
        for note in root.findall(".//cbc:Note", ns):
            if note.get("languageLocaleID") == "1000" and note.text:
                importe_letras = note.text
                break
        if not importe_letras:
            importe_letras = "SON: "

        # Totales
        total = get(".//cac:LegalMonetaryTotal/cbc:PayableAmount")
        
        # We need gravado, inafecto, exonerado, etc.
        gravado = "0.00"
        inafecto = "0.00"
        exonerado = "0.00"
        igv = "0.00"
        
        for tax_subtotal in root.findall(".//cac:TaxTotal/cac:TaxSubtotal", ns):
            tax_scheme = tax_subtotal.find(".//cac:TaxScheme/cbc:ID", ns)
            tax_amt = tax_subtotal.find("cbc:TaxAmount", ns)
            tax_base = tax_subtotal.find("cbc:TaxableAmount", ns)
            
            if tax_scheme is not None and tax_scheme.text == "1000":  # IGV
                igv = tax_amt.text if tax_amt is not None else "0.00"
                gravado = tax_base.text if tax_base is not None else "0.00"
            elif tax_scheme is not None and tax_scheme.text == "9997":  # Exonerado
                exonerado = tax_base.text if tax_base is not None else "0.00"
            elif tax_scheme is not None and tax_scheme.text == "9998":  # Inafecto
                inafecto = tax_base.text if tax_base is not None else "0.00"

        # Items
        items = []
        for invoice_line in root.findall(".//cac:InvoiceLine", ns):
            desc = invoice_line.find(".//cac:Item/cbc:Description", ns)
            qty = invoice_line.find(".//cbc:InvoicedQuantity", ns)
            unit_code = qty.get("unitCode") if qty is not None else "NIU"
            
            # Map unitCode
            unidad_medida = "UNIDAD" if unit_code in ["NIU", "EA"] else "KGS" if unit_code == "KGM" else unit_code
            
            price = invoice_line.find(".//cac:Price/cbc:PriceAmount", ns)
            item_codigo = invoice_line.find(".//cac:Item/cac:SellersItemIdentification/cbc:ID", ns)
            
            items.append({
                "descripcion": desc.text if desc is not None else "",
                "cantidad": qty.text if qty is not None else "1",
                "unidad_medida": unidad_medida,
                "codigo": item_codigo.text if item_codigo is not None else "-",
                "precio_unitario": price.text if price is not None else "0.00",
                "icbper": "0.00"
            })

        return {
            "emisor": {"ruc": emisor_ruc, "razon_social": emisor_razon, "direccion": direccion_emisor},
            "receptor": {"ruc": receptor_ruc, "razon_social": receptor_razon, "direccion": direccion_receptor},
            "comprobante": {
                "tipo_str": tipo_str,
                "serie": serie,
                "numero": numero,
                "fecha": fecha,
                "forma_pago": forma_pago,
                "moneda": moneda,
                "moneda_simbolo": moneda_simbolo,
                "observacion": "-",
                "importe_letras": importe_letras
            },
            "items": items,
            "totales": {
                "descuento_global": "0.00",
                "gravado": gravado,
                "inafecto": inafecto,
                "exonerado": exonerado,
                "gratuito": "0.00",
                "exportacion": "0.00",
                "otros_tributos": "0.00",
                "otros_cargos": "0.00",
                "isc": "0.00",
                "igv": igv,
                "icbper": "0.00",
                "redondeo": "0.00",
                "total": total
            }
        }
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return {}

async def generate_invoice_pdf_from_xml(xml_bytes: bytes, output_path: str):
    """Generates an aesthetic PDF invoice from SUNAT XML."""
    data = parse_sunat_xml(xml_bytes)
    if not data:
        raise ValueError("Failed to parse XML or empty data.")
        
    template = env.get_template("invoice_template.html")
    html_content = template.render(data=data)
    await _html_to_pdf(html_content, output_path)

async def generate_client_report_pdf(report_data: Dict[str, Any], output_path: str):
    """Generates a financial/SIRE report PDF for a client."""
    template = env.get_template("report_template.html")
    html_content = template.render(data=report_data)
    await _html_to_pdf(html_content, output_path)


async def generate_financial_report_pdf(report_data: Dict[str, Any], output_path: str):
    """
    Generates the full financial report PDF (mirrors the Dashboard page):
    KPIs, distribution by comprobante type, balance, top clients/suppliers,
    recent movements and incomplete-processing alerts. The branded header
    (logo + client + periodo) and a standard "Página X de Y" footer repeat
    on every page via Playwright's print header/footer, not just page 1.
    """
    logo_base64 = _get_logo_base64()
    html_content = env.get_template("financial_report_template.html") \
        .render(logo_base64=logo_base64, **report_data)
    header_html = env.get_template("financial_report_header.html") \
        .render(logo_base64=logo_base64, **report_data)
    footer_html = env.get_template("financial_report_footer.html").render()

    await _html_to_pdf(
        html_content, output_path,
        header_template=header_html,
        footer_template=footer_html,
    )
