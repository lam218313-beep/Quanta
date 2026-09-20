"""SUNAT XML/PDF Scraper – Downloads CPEs from 'Consulta de Comprobantes de Pago'.

This scraper navigates the SUNAT SOL portal to the section where comprobantes
(received or emitted) can be listed and downloaded as XML or PDF.

Menu path:  Comprobantes de pago → Comprobantes de Pago → Consulta de
            Comprobantes de Pago → Nueva Consulta de comprobantes de pago
Code:       11.38.1.1.1

Usage:
  1) Run automation_scraper.py to login manually and save cookies.
  2) Use run_batch() from sire_xml_scrape_cli.py for batch downloads.
"""

import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable, Literal, Optional, List

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

MENU_URL = "https://e-menu.sunat.gob.pe/cl-ti-itmenu/MenuInternet.htm"

# Menu code for "Nueva Consulta de comprobantes de pago"
CONSULTA_CPE_CODE = "11.38.1.1.1"

DownloadPrefer = Literal["xml", "pdf", "either"]


# ---------------------------------------------------------------------------
# Serie-prefix → tipo inference
# ---------------------------------------------------------------------------

# En el sistema electrónico de SUNAT, el prefijo de la serie define inequívocamente
# el tipo de comprobante. Cuando el tipo del SIRE TXT no coincide con el prefijo de
# la serie, usamos el prefijo como fuente de verdad.
_SERIE_PREFIX_TO_TIPO: list[tuple[str, str]] = [
    # (prefijo_upper, tipo_sunat)
    # --- Notas de Crédito electrónicas ---
    ("EC",  "07"),  # Nota Crédito para documentos especiales
    ("BE",  "07"),  # Nota Crédito sobre Boleta
    # ("E",   "07"),  # Removed: E001 is often used for Facturas Electrónicas (e.g. from OSEs/airlines)
    # --- Notas de Débito electrónicas ---
    ("BD",  "08"),  # Nota Débito sobre Boleta
    ("FD",  "08"),  # Nota Débito sobre Factura
    ("D",   "08"),  # Nota Débito genérica
    # --- Recibos por Honorarios ---
    ("RH",  "02"),
    ("ER",  "02"),  # e-RxH
    # --- Boletas electrónicas ---
    ("BB",  "03"),
    ("B",   "03"),  # B001, B002...
    # --- Facturas electrónicas ---
    ("FF",  "01"),
    ("F",   "01"),  # F001, F002...
]


def _infer_tipo_from_serie(serie: str, tipo_original: str) -> str:
    """Si el prefijo de la serie define un tipo diferente al registrado en SIRE,
    retorna el tipo correcto para el portal SUNAT. De lo contrario, retorna el original."""
    serie_upper = serie.strip().upper()
    for prefix, tipo_inferred in _SERIE_PREFIX_TO_TIPO:
        if serie_upper.startswith(prefix):
            if tipo_inferred != tipo_original:
                print(
                    f"   [tipo-fix] Serie '{serie}' -> tipo inferido '{tipo_inferred}' "
                    f"(SIRE dijo '{tipo_original}')"
                )
            return tipo_inferred
    return tipo_original  # serie sin prefijo electrónico conocido


async def _auto_login_with_browser(browser, ruc: str) -> bool:
    """Intenta hacer login en SUNAT usando el browser ya abierto para evitar deadlocks de Playwright."""
    from app.brain.db.supabase_client import get_supabase
    
    print(f"🚀 Intentando Auto-Login interno para RUC {ruc}...")
    context = await browser.new_context(user_agent=_default_user_agent())
    page = await context.new_page()
    try:
        await page.goto("https://e-menu.sunat.gob.pe/cl-ti-itmenu/MenuInternet.htm")
        await page.wait_for_load_state('domcontentloaded')
        
        supabase = get_supabase()
        resp = supabase.table("clientes").select("usuario_sol, clave_sol").eq("ruc", ruc).execute()
        if not resp.data or not resp.data[0].get("usuario_sol"):
            print(f"❌ No se encontraron credenciales en BD para {ruc}")
            return False
            
        usuario = resp.data[0].get("usuario_sol")
        clave = resp.data[0].get("clave_sol")
        
        # Rellenar con pausas para asegurar que los eventos JS de SUNAT registren el input
        await page.locator("#txtRuc").fill(ruc)
        await asyncio.sleep(0.5)
        await page.locator("#txtUsuario").fill(usuario)
        await asyncio.sleep(0.5)
        await page.locator("#txtContrasena").fill(clave)
        await asyncio.sleep(0.5)
        
        # A veces el botón btnAceptar está cubierto o desactivado temporalmente. 
        # Usamos evaluate para forzar el click a nivel de DOM.
        await page.evaluate("document.getElementById('btnAceptar').click()")
        print("   Botón Aceptar presionado (vía JS). Esperando redirección...")
        
        try:
            # Intento inicial corto para ver si carga directo o sale la pantalla de código
            try:
                await page.wait_for_url("**/MenuInternet.htm*", timeout=5000)
                print("✅ Auto-Login exitoso! Sesión generada.")
            except Exception:
                # Revisar si apareció la nueva pantalla de autenticación "Continuar sin código"
                if await page.locator("#btnWithOutCode").count() > 0:
                    print("   [Workaround] Pantalla 'Método de Autenticación' detectada. Seleccionando 'Continuar sin código'...")
                    await page.click("#btnWithOutCode")
                
                # Esperar al menú real
                await page.wait_for_url("**/MenuInternet.htm*", timeout=20000)
                print("✅ Auto-Login exitoso! Sesión generada.")
                
        except Exception as e:
            print(f"⚠️ Timeout esperando MenuInternet.htm: {e}")
            print(f"   URL actual: {page.url}")
            print(f"   Título: {await page.title()}")
            
            # WORKAROUND: Fallbacks en caso siga trabado
            if await page.locator("#btnWithOutCode").count() > 0:
                print("   [Workaround] Pantalla 'Método de Autenticación' aún presente. Intentando click...")
                try:
                    await page.click("#btnWithOutCode")
                    await page.wait_for_url("**/MenuInternet.htm*", timeout=15000)
                    print("✅ Auto-Login exitoso (después del workaround btnWithOutCode)!")
                except Exception as ex:
                    print(f"   [Workaround] Falló el click: {ex}")
            elif "api-seguridad.sunat.gob.pe" in page.url and "code=" in page.url:
                print("   [Workaround] Detectada pantalla intermedia de SUNAT. Forzando submit del formulario oculto...")
                try:
                    await page.evaluate("document.forms[0].submit()")
                    await page.wait_for_url("**/MenuInternet.htm*", timeout=15000)
                    print("✅ Auto-Login exitoso (después del workaround)!")
                except Exception as ex:
                    print(f"   [Workaround] Falló el submit forzado: {ex}")
            
            try:
                body_text = await page.evaluate("document.body.innerText")
                print(f"   Texto en pantalla: {body_text[:1000]}")
                # Imprimir valores reales de los inputs para ver si se llenaron
                inputs = await page.evaluate("() => { return 'RUC:' + document.getElementById('txtRuc').value + ' USR:' + document.getElementById('txtUsuario').value; }")
                print(f"   Campos: {inputs}")
            except:
                pass
            error_msg = await page.evaluate("() => { const el = document.querySelector('.error-message, .alert-danger, #msgError, .modal-body'); return el ? el.innerText : ''; }")
            if error_msg:
                print(f"   Mensaje de error: {error_msg}")
        
        cookies = await context.cookies()
        if len(cookies) > 5:
            filepath = Path(__file__).parent / f"sunat_session_{ruc}.json"
            with open(filepath, "w") as f:
                json.dump(cookies, f, indent=4)
            return True
        return False
    except Exception as e:
        print(f"❌ Error en Auto-Login: {e}")
        return False
    finally:
        await context.close()


# Tipos alternativos a probar cuando el tipo original no encuentra el comprobante.
# Clave: tipo original → lista de tipos alternativos en orden de prioridad.
_TIPO_FALLBACKS: dict[str, list[str]] = {
    "01": ["07", "08"],          # Factura -> NC sobre Factura, ND sobre Factura
    "03": ["07", "08"],          # Boleta  -> NC sobre Boleta,  ND sobre Boleta
    "07": ["01", "03", "87"],   # NC -> Factura, Boleta, NC especial
    "08": ["01", "03", "88"],   # ND -> Factura, Boleta, ND especial
    "02": ["01"],               # RxH -> Factura (casos raros de OSE)
    "30": ["01", "04"],         # Liquidacion -> Factura, Liq. compra
    "42": ["01"],               # Doc. de pago -> Factura
    "50": [],                   # DUA Importacion -> sin fallback (aduanas)
    "52": [],                   # Despacho simplificado -> sin fallback
    "53": [],                   # Declaracion mensajeria -> sin fallback
}


@dataclass(frozen=True)
class CpeQuery:
    """A single CPE to look up / download."""
    ruc_emisor: str
    tipo: str       # "01"=Factura, "03"=Boleta, "07"=NC, "08"=ND
    serie: str
    numero: str
    importe: str    # Total amount (for validation)
    fecha: str      # dd/mm/yyyy
    period: str = ""    # YYYYMM for output organization
    book: str = ""      # purchases | sales
    car_sunat: str = ""
    ruc_cliente: str = "" # Required for multi-tenant sessions
    razon_social_cliente: str = "" # Required for folder naming


# ---------------------------------------------------------------------------
# Cookie / session helpers
# ---------------------------------------------------------------------------

def _load_sunat_session_cookies(ruc: str) -> list[dict]:
    cookie_file = os.path.join(os.path.dirname(__file__), f"sunat_session_{ruc}.json")
    if not os.path.exists(cookie_file):
        # Fallback to default for backwards compatibility
        cookie_file = os.path.join(os.path.dirname(__file__), "sunat_session.json")
        if not os.path.exists(cookie_file):
            raise FileNotFoundError(
                f"Session file for RUC {ruc} not found. Run automation_scraper.py --ruc {ruc} first."
            )
    with open(cookie_file, "r") as f:
        return json.load(f)


def _default_user_agent() -> str:
    return (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )


# ---------------------------------------------------------------------------
# Navigation helpers
# ---------------------------------------------------------------------------

async def _dismiss_overlays(page):
    """Remove known campaign/modal overlays that block clicks."""
    for sel in ("#divModalCampana", "#divModalCampanaBak"):
        try:
            if await page.locator(sel).is_visible(timeout=500):
                print(f"   Overlay detected: {sel}. Removing...")
                await page.evaluate(
                    f"document.querySelector('{sel}') && document.querySelector('{sel}').remove()"
                )
                await asyncio.sleep(0.3)
        except Exception:
            pass


async def _navigate_to_consulta_cpe(page):
    """Navigate from the SUNAT SOL main menu to the CPE query form.

    Uses the JavaScript function ``ejecuta()`` with menu code 11.38.1.1.1
    to open "Nueva Consulta de comprobantes de pago" inside #iframeApplication.
    """
    print("Navigating to Consulta de Comprobantes de Pago...")
    await page.wait_for_load_state("networkidle")
    await _dismiss_overlays(page)

    old_pages = list(page.context.pages)
    # Click the menu item natively using jQuery (to trigger their exact internal routing)
    try:
        await page.evaluate("$('#nivel4_11_38_1_1_1').click()")
    except Exception as e:
        print(f"   JS click() raised: {e}")

    await asyncio.sleep(4)

    # Check if a new page/tab opened
    new_pages = list(page.context.pages)
    if len(new_pages) > len(old_pages):
        page = new_pages[-1]

    await page.wait_for_load_state()

    # Resolve the iframe that hosts the application
    iframe_sel = "#iframeApplication"
    try:
        await page.wait_for_selector(iframe_sel, state="attached", timeout=15000)
    except Exception:
        # Fallback: sometimes there's an intermediate frame
        pass

    eh = await page.query_selector(iframe_sel)
    frame = await eh.content_frame() if eh else None
    if not frame:
        raise RuntimeError("Could not resolve #iframeApplication frame")

    # Wait for the form to appear (the consulta page should have a date filter or a table)
    # The form may have different layouts, let's wait for something generic
    try:
        await frame.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass

    # INYECTAR MUTATION OBSERVER PARA AUTO-CERRAR MODALES DE ERROR DE SUNAT INMEDIATAMENTE
    auto_closer_js = """
    () => {
        if (window._sunatAutoCloserInjected) return;
        window._sunatAutoCloserInjected = true;
        
        const observer = new MutationObserver((mutations) => {
            const btns = document.querySelectorAll('button.btn-primary, .swal2-confirm');
            for (const btn of btns) {
                const text = (btn.innerText || '').trim().toLowerCase();
                if (text === 'aceptar' && btn.offsetParent !== null) {
                    // Check if it's inside an error modal (or just click it anyway to unblock)
                    console.log('Botón Aceptar (Modal) auto-clickeado por script inyectado!');
                    btn.click();
                }
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }
    """
    try:
        await page.evaluate(auto_closer_js)
        await frame.evaluate(auto_closer_js)
    except Exception as e:
        print(f"   [debug] error inyectando auto-closer: {e}")

    await asyncio.sleep(2)
    return page, frame


async def _setup_filters_and_search(frame, *, ruc: str, fecha_desde: str, fecha_hasta: str):
    """Fill the search form inside the CPE query page and click 'Buscar'.

    Parameters
    ----------
    frame : Playwright Frame inside #iframeApplication
    ruc : The RUC to search (emisor or receptor depending on context)
    fecha_desde, fecha_hasta : dd/mm/yyyy date range
    """
    print(f"   Filtering: {fecha_desde} – {fecha_hasta} | RUC: {ruc}")

    # The "Nueva Consulta" page has various filter fields.
    # Try to fill them, but some might not exist depending on the SUNAT version.

    # Type of search: Recibidos (received) or Emitidos (sent)
    # Try to click the "Recibidos" tab/radio if available
    for sel in [
        "input[value='recibidos']",
        "label:has-text('Recibidos')",
        "#rbRecibidos",
        "input[name='tipoConsulta'][value='2']",
    ]:
        try:
            if await frame.locator(sel).count() > 0:
                await frame.locator(sel).first.click()
                await asyncio.sleep(0.5)
                break
        except Exception:
            continue

    # Date range
    for sel in ["#fechaDesde", "input[name='fechaDesde']", "#fecDesde", "input[name='fecDesde']"]:
        try:
            if await frame.locator(sel).count() > 0:
                await frame.locator(sel).first.fill(fecha_desde)
                break
        except Exception:
            continue

    for sel in ["#fechaHasta", "input[name='fechaHasta']", "#fecHasta", "input[name='fecHasta']"]:
        try:
            if await frame.locator(sel).count() > 0:
                await frame.locator(sel).first.fill(fecha_hasta)
                break
        except Exception:
            continue

    await asyncio.sleep(0.5)

    # Click Buscar / Consultar
    for sel in [
        "button#btnBuscar",
        "button:has-text('Buscar')",
        "button:has-text('Consultar')",
        "#btnConsultar",
        "input[type='submit']",
        "button.btn-primary",
    ]:
        try:
            if await frame.locator(sel).count() > 0:
                await frame.locator(sel).first.click(timeout=8000)
                break
        except Exception:
            continue

    await asyncio.sleep(3)
    try:
        await frame.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Core: search-and-download for a single CPE via the individual query form
# ---------------------------------------------------------------------------

async def _search_individual(
    *,
    page,
    frame,
    query: CpeQuery,
    out_dir: Path,
    base_name: str,
    prefer: DownloadPrefer,
    debug_dir: Optional[Path] = None,
    tmp_downloads_dir: Optional[Path] = None,
    is_fallback: bool = False,
) -> List[Path]:
    """Fill the individual CPE search form, check results, and download.

    This function handles the 'Consulta Individual' tab inside the
    Consulta de Comprobantes page.
    """
    print(f"Query: {base_name}")

    # Detectar variante del formulario:
    # - Angular puro: input con formcontrolname='rucEmisor' + p-dropdown
    # - Hibrido: input con name='rucEmisor' (sin formcontrolname) + radioBoton id='emitido'
    # - Legacy: campos numRuc, codComp, numeroSerie
    is_angular  = await frame.locator("input[formcontrolname='rucEmisor']").count() > 0
    is_hybrid   = (
        not is_angular
        and await frame.locator("[name='rucEmisor']").count() > 0
        and await frame.locator("#emitido, #recibido").count() > 0
    )

    if is_angular or is_hybrid:
        try:
            if query.book == "sales":
                # Check emitido - capturar si ya estaba checked sin lanzar error
                try:
                    await frame.locator("#emitido").check(force=True)
                except Exception:
                    pass  # ya estaba seleccionado
                await asyncio.sleep(0.5)
                # CAMBIO: Para ventas (emitidos) NO llenamos el RUC receptor.
                # Muchas boletas no tienen receptor (consumidor final sin DNI/RUC)
                # y el portal de SUNAT busca por Serie+Número dentro de los comprobantes
                # propios del contribuyente logueado — el receptor no es necesario.
                print("   [ventas] Modo emitido: buscando solo por Serie/Número (sin RUC receptor).")
            else:
                try:
                    await frame.locator("#recibido").check(force=True)
                except Exception:
                    pass  # ya estaba seleccionado
                await asyncio.sleep(0.5)
                ruc_field = (
                    "input[formcontrolname='rucEmisor']" if is_angular
                    else "[name='rucEmisor']"
                )
                try:
                    await frame.locator(ruc_field).fill(query.ruc_emisor, timeout=2000)
                except Exception:
                    pass
        except Exception as e:
            print(f"   Could not configure Recibido/Emitido and fill RUC: {e}")

        # 3. Tipo Comprobante (PrimeNG dropdown)
        # Bug Fix 1 & 2: mapeo extendido de tipos + timeouts aumentados
        # 3. Tipo Comprobante (PrimeNG dropdown)
        # Bug Fix 1 & 2: mapeo extendido de tipos + timeouts aumentados
        if is_angular:
            try:
                # El formcontrolname exacto ('tipoComprobanteI') puede no existir si
                # SUNAT cambió el nombre del control o si el dropdown aún no terminó
                # de renderizar tras marcar Recibido/Emitido. Intentamos primero el
                # nombre conocido y, si no aparece, cualquier control cuyo nombre
                # contenga 'tipoComprobante' (case-insensitive) antes de rendirnos.
                dropdown = None
                for attempt in range(2):  # el Angular app puede tardar en renderizar bajo carga
                    for tipo_sel in (
                        "p-dropdown[formcontrolname='tipoComprobanteI']",
                        "p-dropdown[formcontrolname*='tipoComprobante' i]",
                    ):
                        candidate = frame.locator(tipo_sel)
                        try:
                            await candidate.first.wait_for(state="visible", timeout=8000)
                            dropdown = candidate.first
                            break
                        except Exception:
                            continue
                    if dropdown is not None:
                        break
                    await asyncio.sleep(1)

                if dropdown is None:
                    # Evidencia: qué formcontrolname existen realmente en la página,
                    # para diagnosticar sin adivinar en el próximo intento.
                    try:
                        all_fcn = await frame.evaluate(
                            "Array.from(document.querySelectorAll('[formcontrolname]'))"
                            ".map(e => e.tagName + ':' + e.getAttribute('formcontrolname'))"
                        )
                        print(f"   WARN: dropdown tipoComprobante no encontrado. Controles en pagina: {all_fcn}")
                    except Exception:
                        pass
                    raise RuntimeError("tipoComprobante dropdown not found on page")

                await dropdown.click(timeout=5000)  # Bug 2: aumentado de 2000 a 5000ms

                # Bug 2: esperar explícitamente a que el panel de opciones sea visible
                try:
                    await frame.wait_for_selector(
                        "p-dropdownitem li", state="visible", timeout=4000
                    )
                except Exception:
                    pass

                await asyncio.sleep(0.5)

                tipo_str = str(query.tipo).strip().zfill(2)
                serie_str = str(query.serie).strip().upper()

                # Parte A: corregir tipo usando el prefijo de la serie cuando SIRE y portal discrepan
                if not is_fallback:
                    tipo_str = _infer_tipo_from_serie(query.serie, tipo_str).zfill(2)
                # Bug 1: Catálogo completo de tipos de comprobante SUNAT (Catálogo N° 01)
                TIPO_TEXT_MAP = {
                    "01": "Factura",
                    "02": "Recibo por Honorarios",
                    "03": "Boleta de Venta",
                    "04": "Liquidación de compra",
                    "05": "Boleto de compañía de aviación",
                    "06": "Carta de porte aéreo",
                    "07": "Nota de Crédito",   # se refina abajo según serie
                    "08": "Nota de Débito",    # se refina abajo según serie
                    "09": "Guía de remisión remitente",
                    "10": "Recibo por arrendamiento",
                    "11": "Póliza de adjudicación",
                    "12": "Ticket o cinta emitida por máquina registradora",
                    "13": "Documentos emitidos por bancos",
                    "14": "Recibo por servicios públicos",
                    "15": "Boletos emitidos por servicios de transporte",
                    "16": "Boletos emitidos por espectáculos públicos",
                    "17": "Documento de atribución",
                    "18": "Documentos emitidos por AFP",
                    "19": "Boleto o entrada por atracciones",
                    "20": "Comprobante de retención",
                    "21": "Conocimiento de embarque",
                    "22": "Comprobante por Operaciones No Habituales",
                    "23": "Póliza de seguro",
                    "24": "Certificado de renta",
                    "25": "Ticket de transporte ferroviario",
                    "26": "Recibo de gas natural",
                    "27": "Factura negociable",
                    "28": "Tarjeta de crédito",
                    "29": "Certificado de depósito",
                    "30": "Liquidación de compra",  # Bug 1: tipo 30 no estaba mapeado
                    "31": "Guía de remisión transportista",
                    "34": "Documento del operador",
                    "35": "Documento del partícipe",
                    "36": "Recibo de haber",
                    "37": "Documentos sustentatorios de operaciones de importación",
                    "40": "Comprobante de percepción",
                    "41": "Comprobante de retención electrónico",
                    "50": "Declaración Única de Aduanas (Importación definitiva)",
                    "52": "Despacho simplificado (Importación)",
                    "53": "Declaración de mensajería",
                    "56": "Declaración Única de Aduanas (Exportación definitiva)",
                    "87": "Nota de crédito especial",
                    "88": "Nota de débito especial",
                    "91": "Comprobante de no domiciliado",
                    "96": "Exceso de crédito fiscal por tasa adicional del IGV",
                    "97": "Nota de crédito - no domiciliado",
                    "98": "Nota de débito - no domiciliado",
                }

                # Refinar tipos 07 y 08 según la letra de la serie
                if tipo_str == "07":
                    if serie_str.startswith("B"):
                        exact_text = "Boleta de Venta - Nota de Crédito"
                    else:
                        exact_text = "Factura - Nota de Crédito"
                elif tipo_str == "08":
                    if serie_str.startswith("B"):
                        exact_text = "Boleta de Venta - Nota de Débito"
                    else:
                        exact_text = "Factura - Nota de Débito"
                else:
                    exact_text = TIPO_TEXT_MAP.get(tipo_str, "")

                selected = False
                if exact_text:
                    # Intento 1: coincidencia exacta
                    item_loc = frame.locator(f"p-dropdownitem li:text-is('{exact_text}')")
                    if await item_loc.count() > 0:
                        await item_loc.first.click(timeout=4000)
                        selected = True

                    if not selected:
                        # Intento 2: coincidencia parcial
                        fallback_loc = frame.locator(f"p-dropdownitem li:has-text('{exact_text}')")
                        if await fallback_loc.count() > 0:
                            await fallback_loc.first.click(timeout=4000)
                            selected = True

                if not selected:
                    # Intento 3 (Bug 1 fallback): buscar por el código numérico directamente en el texto
                    code_loc = frame.locator(f"p-dropdownitem li:has-text('{tipo_str}')")
                    if await code_loc.count() > 0:
                        await code_loc.first.click(timeout=4000)
                        selected = True
                        print(f"   Tipo {tipo_str} seleccionado por código (fallback).")

                if not selected:
                    print(f"   WARN: No se pudo seleccionar tipo {tipo_str} ('{exact_text}') en el dropdown. Continuando sin filtro de tipo.")
                    await frame.evaluate("document.body.click()")

            except Exception as e:
                print(f"   Could not select tipoComprobante: {e}")

        # 4. Serie & Numero
        try:
            serie_field = (
                "input[formcontrolname='serieComprobante']" if is_angular
                else "[name='serieComprobante']"
            )
            numero_field = (
                "input[formcontrolname='numeroComprobante']" if is_angular
                else "[name='numeroComprobante']"
            )
            await frame.locator(serie_field).fill(query.serie, timeout=2000)
            await frame.locator(numero_field).fill(query.numero, timeout=2000)
        except Exception as e:
            print(f"   Could not fill serie/numero: {e}")



    # Selectores del botón Consultar (en orden de prioridad)
    _CONSULTAR_SELS = [
        "#btnConsultar",
        "button:has-text('Consultar')",
        "button:has-text('Buscar')",
        "#btnAceptar",
        "button.btn-primary",
    ]
    # Selectores de spinner/loading que indica que SUNAT sigue procesando
    _LOADING_SELS = [
        "p-progressspinner",
        ".p-progress-spinner",
        ".loading",
        ".spinner",
        "[class*='loading']",
        "[class*='spinner']",
    ]
    # Señales de que ya hay un resultado (modal o tabla visible)
    _RESULT_SELS = [
        ".swal2-popup",          # modal SweetAlert2 con el comprobante
        "app-modal-detalle",     # modal Angular con detalle del CPE
        ".modal.show",           # modal Bootstrap visible
        "button[ngbtooltip*='PDF']",   # botón de descarga PDF
        "button[ngbtooltip*='XML']",   # botón de descarga XML
        ".button-container button",    # contenedor de botones en modal Angular
    ]

    async def _has_result_or_no_result(frm) -> bool:
        """Devuelve True si el portal ya respondió (con resultado o sin él)."""
        try:
            body = await frm.evaluate("document.body.innerText")
        except Exception:
            body = ""
        no_result_phrases = [
            "No se encontraron registros",
            "0 de un total de 0",
            "No existen datos para los criterios",
            "El comprobante no existe",
            "No existe información",
            "No hay resultados para la consulta realizada",
            "no hay resultado",
            "sin resultados",
        ]
        if any(p.lower() in body.lower() for p in no_result_phrases):
            return True  # Respondió con "no encontrado"
        for sel in _RESULT_SELS:
            try:
                if await frm.locator(sel).count() > 0:
                    return True  # Hay un modal/resultado visible
            except Exception:
                continue
        return False

    async def _is_still_loading(frm) -> bool:
        """Devuelve True si hay un spinner de carga activo en el frame."""
        for sel in _LOADING_SELS:
            try:
                if await frm.locator(sel).is_visible(timeout=300):
                    return True
            except Exception:
                continue
        return False

    # CAMBIO: Loop de reintento para el botón Consultar (máx. 4 intentos).
    # Cuando SUNAT se queda cargando infinitamente, un segundo click/Enter
    # en Consultar desbloquea el portal y muestra el resultado.
    MAX_CONSULTAR_RETRIES = 4
    consultar_clicked = False

    for intento in range(1, MAX_CONSULTAR_RETRIES + 1):
        # 1. Hacer click en Consultar (solo si no se hizo ya, o es reintento)
        for sel in _CONSULTAR_SELS:
            try:
                if await frame.locator(sel).count() > 0:
                    # El usuario indicó que hacer click a veces falla si está bloqueado, pero dar Tab (focus) y Enter funciona.
                    # CONFIRMADO MANUALMENTE: un solo Enter deja a SUNAT "cargando" indefinidamente
                    # con bastante frecuencia; lo que realmente lo destraba es dar Enter varias
                    # veces seguidas en rápida sucesión (~3 Enters en 1-1.5s), no un solo click
                    # seguido de esperas largas. Replicamos exactamente esa ráfaga.
                    btn = frame.locator(sel).first
                    await btn.evaluate("node => node.focus()")
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(0.5)
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(0.5)
                    await page.keyboard.press("Enter")

                    consultar_clicked = True
                    if intento > 1:
                        print(f"   [retry-consultar] Intento {intento}/{MAX_CONSULTAR_RETRIES}: re-click en Consultar (ráfaga de 3 Enters).")
                    break
            except Exception:
                continue

        if not consultar_clicked:
            break  # No se encontró el botón — salir del loop

        # 2. Esperar medio segundo para ver si salió la factura (indicación del usuario)
        await asyncio.sleep(0.5)
        if await _has_result_or_no_result(frame):
            break
            
        # 3. Si no salió inmediatamente, esperar 2.5 seg más (total 3 seg)
        await asyncio.sleep(2.5)

        # 2.5 Verificar si salió un modal de error (Ej: "Error del Servidor" -> "Aceptar") y cerrarlo
        # SUNAT a veces lanza este modal en el iframe y otras veces en la página principal (ngb-modal-window)
        try:
            for ctx in [page, frame]:
                accept_btn = ctx.locator("button:has-text('Aceptar'), .swal2-confirm")
                if await accept_btn.count() > 0 and await accept_btn.first.is_visible():
                    print(f"   [retry-consultar] Apareció modal de error (Servidor saturado). Haciendo click en Aceptar...")
                    await accept_btn.first.click(timeout=1000)
                    await asyncio.sleep(1)
                    break
        except Exception as e:
            print(f"   [debug] error cerrando modal: {e}")
            pass

        # 3. Verificar si ya hay respuesta del portal
        if await _has_result_or_no_result(frame):
            break  # Portal respondió correctamente — listo

        # 4. Si sigue cargando (spinner activo), esperar un poco más antes de reintentar
        if await _is_still_loading(frame):
            print(f"   [retry-consultar] Portal sigue cargando tras intento {intento}. Reintentando...")
            await asyncio.sleep(2)
            # Continuar con el siguiente intento (re-click)
        else:
            # No hay spinner pero tampoco resultado — puede ser un estado intermedio
            # Esperar un segundo adicional y verificar de nuevo
            await asyncio.sleep(1)
            if await _has_result_or_no_result(frame):
                break
            if intento < MAX_CONSULTAR_RETRIES:
                print(f"   [retry-consultar] Sin respuesta clara tras intento {intento}. Reintentando...")
            # continuar con el siguiente intento

    # Check if we got a result
    try:
        body_text = await frame.evaluate("document.body.innerText")
    except Exception:
        body_text = ""

    # --- Detectar saturación del servidor SUNAT ("Error del Servidor") o carga aún en curso ---
    # Evidencia real: TODAS las capturas de debug de casos marcados no_descargable hasta ahora
    # muestran el modal "Error del Servidor... por favor reintentar en 5 minutos" con el spinner
    # ngx-spinner ("Cargando...") todavía visible. El bot agotaba sus 4 reintentos cortos (~3s
    # cada uno), asumía found=True porque ese texto no coincide con not_found_texts, y al no
    # encontrar botones (la página nunca terminó de cargar) lo marcaba NO_DESCARGABLE — un
    # estado TERMINAL que sire_bot_orchestrator.py nunca vuelve a reintentar. El comprobante sí
    # existe y sí es descargable; SUNAT solo estaba saturado por el volumen de consultas.
    server_busy_texts = [
        "error del servidor",
        "no se puede acceder a los servicios de sunat",
        "por favor reintentar en 5 minutos",
    ]
    async def _still_server_busy() -> bool:
        try:
            txt = await frame.evaluate("document.body.innerText")
        except Exception:
            txt = ""
        if any(t in txt.lower() for t in server_busy_texts):
            return True
        try:
            return await frame.locator("ngx-spinner, .loading-text").first.is_visible(timeout=300)
        except Exception:
            return False

    is_server_busy = await _still_server_busy()

    if is_server_busy:
        # CONFIRMADO MANUALMENTE: cuando queda "atascado" así, no basta con esperar — hay que
        # forzarlo con Enters seguidos. Antes de rendirnos (server_busy -> reintenta mañana),
        # probamos exactamente esa técnica una vez más aquí, ya con el modal de error cerrado.
        print(f"   [server-busy] SUNAT saturado o carga incompleta tras los reintentos. Forzando con ráfaga extra de Enters: {base_name}")
        try:
            for ctx in [page, frame]:
                accept_btn = ctx.locator("button:has-text('Aceptar'), .swal2-confirm")
                if await accept_btn.count() > 0 and await accept_btn.first.is_visible():
                    await accept_btn.first.click(timeout=1000)
                    await asyncio.sleep(0.3)
        except Exception:
            pass

        # Re-enfocar el botón Consultar antes de la ráfaga: el foco se pudo perder al
        # cerrar el modal de "Aceptar", y Enter sin foco en el botón no dispara nada.
        try:
            for sel in _CONSULTAR_SELS:
                if await frame.locator(sel).count() > 0:
                    await frame.locator(sel).first.evaluate("node => node.focus()")
                    break
        except Exception:
            pass

        for _ in range(3):
            try:
                await page.keyboard.press("Enter")
            except Exception:
                pass
            await asyncio.sleep(0.5)
        await asyncio.sleep(1.5)

        is_server_busy = await _still_server_busy()

    if is_server_busy:
        print(f"   [server-busy] La ráfaga de Enters no logró destrabarlo: {base_name}")
        if debug_dir:
            debug_dir.mkdir(parents=True, exist_ok=True)
            try:
                await page.screenshot(path=str(debug_dir / f"server_busy-{base_name}.png"))
                html = await frame.content()
                (debug_dir / f"server_busy-{base_name}.html").write_text(html, encoding="utf-8")
            except Exception:
                pass
        # Cerrar cualquier modal de error residual antes de continuar con el siguiente comprobante
        try:
            accept_btn = frame.locator("button:has-text('Aceptar'), .swal2-confirm")
            if await accept_btn.count() > 0:
                await accept_btn.first.click(timeout=1000)
        except Exception:
            pass
        return "server_busy"

    # The result panel varies heavily between Angular and legacy apps.
    # Assume found unless we see explicit "no results" text
    found = True

    not_found_texts = [
        "No se encontraron registros",
        "0 de un total de 0",
        "No existen datos para los criterios",
        "El comprobante no existe",
        "No existe información",
        "No hay resultados para la consulta realizada",  # Modal de error del portal Angular
        "no hay resultado",
        "sin resultados",
    ]
    if any(t.lower() in body_text.lower() for t in not_found_texts):
        found = False

    if not found:
        # Save debug artifacts
        if debug_dir:
            debug_dir.mkdir(parents=True, exist_ok=True)
            try:
                await page.screenshot(path=str(debug_dir / f"not_found-{base_name}.png"))
                html = await frame.content()
                (debug_dir / f"not_found-{base_name}.html").write_text(html, encoding="utf-8")
            except Exception:
                pass
        return []

    print(f"   Found: {base_name}")
    
    # Dump result modal HTML for debugging
    if debug_dir:
        try:
            debug_dir.mkdir(parents=True, exist_ok=True)
            html = await frame.content()
            (debug_dir / f"_debug_result_modal.html").write_text(html, encoding="utf-8")
        except Exception:
            pass

    # Try to find XML/PDF download button
    xml_sels = [
        "a:has-text('XML')", "button:has-text('XML')",
        "[title*='XML']", "[onclick*='xml']", "[onclick*='XML']",
        "button[ngbtooltip*='XML']", "button[ngbtooltip*='xml']",
        "button:has(i.fa-file-code)", "button:has(i.fa-file-excel)",
        ".button-container button:nth-of-type(2)", # Angular modal (2nd button)
    ]
    pdf_sels = [
        "a:has-text('PDF')", "button:has-text('PDF')",
        "[title*='PDF']", "[onclick*='pdf']", "[onclick*='PDF']",
        "button[ngbtooltip*='PDF']", "button[ngbtooltip*='pdf']",
        "button:has(i.fa-file-pdf)",
        ".button-container button:nth-of-type(1)", # Angular modal (1st button)
    ]
    fallback_sels = [
        "a:has-text('Descargar')", "button:has-text('Descargar')",
        "button[ngbtooltip*='Descargar']",
        "a:has-text('Imprimir')", "button[ngbtooltip*='Imprimir']"
    ]

    targets = []

    # BUGFIX: Respetar el orden XML primero, luego PDF.
    # Además, cuando skip_existing ya filtró parcialmente, el out_dir puede
    # tener solo uno de los dos — aquí simplemente recolectamos los botones disponibles.
    if prefer in ("xml", "either"):
        # Check XML selectors
        for sel in xml_sels:
            try:
                if await frame.locator(sel).count() > 0:
                    targets.append(("xml", frame.locator(sel).first))
                    break
            except Exception:
                continue

    if prefer in ("pdf", "either"):
        # Check PDF selectors
        for sel in pdf_sels:
            try:
                if await frame.locator(sel).count() > 0:
                    targets.append(("pdf", frame.locator(sel).first))
                    break
            except Exception:
                continue

    # Filtrar targets ya descargados para evitar re-descarga innecesaria
    # (cuando skip_existing=True y prefer=either, puede que solo falte uno)
    if targets:
        xml_path_check = out_dir / "xml" / f"{base_name}.xml"
        zip_path_check = out_dir / "xml" / f"{base_name}.zip"
        pdf_path_check = out_dir / "pdf" / f"{base_name}.pdf"
        filtered_targets = []
        for ft, loc in targets:
            if ft == "xml" and (xml_path_check.exists() or zip_path_check.exists()):
                print(f"   [skip-xml] XML ya existe localmente, omitiendo botón XML: {base_name}")
                continue
            if ft == "pdf" and pdf_path_check.exists():
                print(f"   [skip-pdf] PDF ya existe localmente, omitiendo botón PDF: {base_name}")
                continue
            filtered_targets.append((ft, loc))
        targets = filtered_targets

    # Fallback if neither found
    if not targets:
        for sel in fallback_sels:
            try:
                if await frame.locator(sel).count() > 0:
                    targets.append(("fallback", frame.locator(sel).first))
                    break
            except Exception:
                continue

    if not targets:
        print(f"   Comprobante found but NO download button (no_descargable): {base_name}")
        if debug_dir:
            debug_dir.mkdir(parents=True, exist_ok=True)
            try:
                await page.screenshot(path=str(debug_dir / f"no_download-{base_name}.png"))
                html = await frame.content()
                (debug_dir / f"no_download-{base_name}.html").write_text(html, encoding="utf-8")
            except Exception:
                pass
        # Cerrar modal
        try:
            close_btns = frame.locator("button.close, button.close-without-header, button[aria-label='Close']")
            count = await close_btns.count()
            for i in range(count - 1, -1, -1):
                await close_btns.nth(i).click(force=True, timeout=1000)
                await asyncio.sleep(0.3)
        except Exception:
            pass
        # No se encontro boton de descarga con este tipo de comprobante.
        # Retornar centinela para que run_batch decida si probar fallbacks o marcar NO_DESCARGABLE.
        return "no_descargable"


    # Download the files
    downloaded_paths = []
    
    for file_type, target in targets:
        try:
            import time
            import shutil
            
            # SNAPSHOT: record what's already in tmp BEFORE clicking
            # This prevents picking up leftover files from a previous query
            existing_in_tmp = set()
            if tmp_downloads_dir and tmp_downloads_dir.exists():
                existing_in_tmp = {f.name for f in tmp_downloads_dir.glob("*")}
            
            # AUMENTAMOS EL TIMEOUT A 30 SEGUNDOS (30000ms) PORQUE SUNAT ES LENTO CON LOS ZIP
            download_task = asyncio.ensure_future(
                page.context.wait_for_event("download", timeout=30000)
            )

            await target.click()
            
            # Check for the warning modal "El archivo se ha descargado previamente"
            try:
                accept_btn = frame.locator("button:has-text('Aceptar'), .swal2-confirm")
                if await accept_btn.count() > 0:
                    await accept_btn.first.click(timeout=2000)
            except Exception:
                pass
                
            # Active polling loop for Chromium silent downloads
            recovered = False
            start_wait = time.time()
            
            # AUMENTAMOS EL BUCLE A 30 SEGUNDOS
            while time.time() - start_wait < 30: 
                if download_task.done() and not download_task.cancelled() and not isinstance(download_task.exception(), Exception):
                    break # The official download event fired!
                    
                if tmp_downloads_dir and tmp_downloads_dir.exists():
                    files = list(tmp_downloads_dir.glob("*"))
                    # KEY FIX: Only consider files that WEREN'T there before we clicked
                    new_files = [f for f in files if f.name not in existing_in_tmp]
                    if new_files:
                        new_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                        newest = new_files[0]
                        # Check: not a temp file, and size > 1KB (fully written)
                        file_stat = newest.stat()
                        if not newest.name.endswith('.crdownload') and file_stat.st_size > 1024:
                            
                            # SOLUCIÓN: Detectar la extensión real (sea .zip, .xml, o .pdf)
                            ext_real = newest.suffix.lower()
                            if not ext_real or ext_real == '.bin':
                                ext_real = f".{file_type}" if file_type != "fallback" else ".pdf"

                            # Rutear a la carpeta correcta basado en la extensión real
                            if ext_real in (".xml", ".zip"):
                                subfolder = "xml"
                            elif ext_real == ".pdf":
                                subfolder = "pdf"
                            else:
                                subfolder = "pdf" if file_type in ("pdf", "fallback") else "xml"
                                
                            final_dir = out_dir / subfolder
                            final_dir.mkdir(parents=True, exist_ok=True)
                            final_path = final_dir / f"{base_name}{ext_real}"
                            
                            shutil.copy2(newest, final_path)
                            
                            # Verify the copy actually worked (not zero bytes)
                            if os.path.exists(final_path) and os.path.getsize(final_path) > 0:
                                try:
                                    newest.unlink()
                                except Exception:
                                    pass  # Windows may lock the file - that's OK, it's already copied
                                    
                                downloaded_paths.append(final_path)
                                recovered = True
                                print(f"   Recovered downloaded file actively: {newest.name} -> guardado como {final_path.name}")
                                
                                # Cancel the official wait task since we got the file
                                if not download_task.done():
                                    download_task.cancel()
                                break
                            else:
                                print(f"   Warning: copy of {newest.name} failed or resulted in empty file. Retrying...")
                await asyncio.sleep(1)

            if recovered:
                await asyncio.sleep(0.5)
                continue # move to next target
                
            # If we reach here and it's not recovered, maybe the official download event succeeded
            try:
                download = await download_task
                suggested = download.suggested_filename or "download"
                
                # SOLUCIÓN: Respetar la extensión del archivo oficial sugerido por SUNAT
                ext = os.path.splitext(suggested)[1] or f".{file_type}"
                
                if ext.lower() == ".bin" and file_type != "fallback":
                    ext = f".{file_type}"
                    
                ext_lower = ext.lower()
                
                # Rutear a la carpeta correcta
                if ext_lower in (".xml", ".zip"):
                    subfolder = "xml"
                elif ext_lower == ".pdf":
                    subfolder = "pdf"
                else:
                    subfolder = "pdf" if file_type in ("pdf", "fallback") else "xml"
                    
                final_dir = out_dir / subfolder
                final_dir.mkdir(parents=True, exist_ok=True)
                
                final_path = final_dir / f"{base_name}{ext}"
                await download.save_as(str(final_path))
                downloaded_paths.append(final_path)
                print(f"   Downloaded officially: {final_path.name}")
                await asyncio.sleep(0.5)
            except Exception as wait_err:
                print(f"   Download failed for {file_type}: Timeout or error -> {wait_err}")

        except Exception as e:
            print(f"   Download click or process failed for {file_type}: {e}")
            
    # Close modal for next query
    try:
        close_btns = frame.locator("button.close, button.close-without-header, button[aria-label='Close']")
        count = await close_btns.count()
        for i in range(count - 1, -1, -1):
            await close_btns.nth(i).click(force=True, timeout=1000)
            await asyncio.sleep(0.3)
    except Exception:
        pass
        
    if not downloaded_paths:
        return []

    return downloaded_paths


async def _clear_form(frame, page=None):
    """Click 'Limpiar' to reset the form for the next query and ensure modals are closed."""
    # Force close any open modals using Playwright explicit clicks
    try:
        close_btns = frame.locator("button.close, button.close-without-header, button[aria-label='Close']")
        count = await close_btns.count()
        for i in range(count - 1, -1, -1):
            await close_btns.nth(i).click(force=True, timeout=1000)
            await asyncio.sleep(0.3)
    except Exception:
        pass

    for sel in [
        "#btnLimpiar",
        "button:has-text('Limpiar')",
        "button.p-button-outlined", # Common PrimeNG secondary button class
    ]:
        try:
            if await frame.locator(sel).count() > 0:
                await frame.locator(sel).first.click(timeout=3000)
                await asyncio.sleep(1)
                return
        except Exception:
            continue


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------
import re

def _sanitize_folder_name(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

async def run_batch(
    queries: Iterable[CpeQuery],
    *,
    outdir: str,
    prefer: DownloadPrefer = "xml",
    headless: bool = False,
    skip_existing: bool = True,
    limit: int = 0,
) -> list[dict]:
    """Open browser, navigate to Consulta de Comprobantes, and download each CPE.

    Returns a list of result dicts with keys:
      status, ruc_emisor, tipo, serie, numero, period, book, path, error
    """
    out_base = Path(outdir).expanduser().resolve()
    results: list[dict] = []

    # Group queries by ruc_cliente so we can load the correct session cookie
    from collections import defaultdict
    queries_by_client = defaultdict(list)
    for q in queries:
        queries_by_client[q.ruc_cliente].append(q)

    async with async_playwright() as p:
        # BUGFIX: proceso-especifico (PID), no compartido. Antes esto era
        # siempre out_base/"tmp_downloads" para TODOS los clientes; con
        # concurrency>1 en daily_sync.py, varios subprocesos de
        # sire_bot_orchestrator.py corren en paralelo y cada uno lanza su
        # propio Chromium apuntando a esa MISMA carpeta compartida. La
        # heuristica de "que archivo nuevo aparecio despues del click" en
        # _search_individual entonces podia recoger el archivo de OTRO
        # cliente que llegara casi al mismo tiempo, subiendolo con el
        # nombre/extension equivocado (ej. un PDF terminando guardado bajo
        # la ruta que se registra como XML). Con PID cada proceso tiene su
        # propia carpeta y nunca se cruzan.
        tmp_downloads_dir = out_base / "tmp_downloads" / f"pid{os.getpid()}"
        tmp_downloads_dir.mkdir(parents=True, exist_ok=True)
        browser = await p.chromium.launch(headless=headless, downloads_path=str(tmp_downloads_dir))
        
        for ruc_cliente, client_queries in queries_by_client.items():
            print(f"\n--- Processing {len(client_queries)} queries for client {ruc_cliente} ---")
            
            try:
                cookies = _load_sunat_session_cookies(ruc_cliente)
            except FileNotFoundError as e:
                print(f"Sesión no encontrada para {ruc_cliente}. Intentando auto-login...")
                success = await _auto_login_with_browser(browser, ruc_cliente)
                if success:
                    cookies = _load_sunat_session_cookies(ruc_cliente)
                else:
                    for q in client_queries:
                        results.append(_result_dict(q, "error", error=f"No session cookies and autologin failed"))
                    continue

            context = await browser.new_context(
                user_agent=_default_user_agent(),
                accept_downloads=True,
            )
            await context.add_cookies(cookies)

            page = await context.new_page()
            print(f"Navigating to SUNAT Main Menu for {ruc_cliente}...")
            await page.goto(MENU_URL)
            await _dismiss_overlays(page)

            # Navigate to the Consulta de Comprobantes form
            # AISLADO por cliente: si la sesión expiró, marcamos sus comprobantes
            # como error y continuamos con el siguiente cliente sin matar el batch.
            try:
                page, frame = await _navigate_to_consulta_cpe(page)
            except Exception as nav_err:
                print(f"   [SESION EXPIRADA/ERROR] Cliente {ruc_cliente}: {nav_err}")
                print(f"   Intentando auto-login automático...")
                await context.close()
                
                success = await _auto_login_with_browser(browser, ruc_cliente)
                if success:
                    cookies = _load_sunat_session_cookies(ruc_cliente)
                    context = await browser.new_context(user_agent=_default_user_agent(), accept_downloads=True)
                    await context.add_cookies(cookies)
                    page = await context.new_page()
                    await page.goto(MENU_URL)
                    await _dismiss_overlays(page)
                    try:
                        page, frame = await _navigate_to_consulta_cpe(page)
                    except Exception as retry_err:
                        print(f"   Auto-login falló: {retry_err}")
                        for q in client_queries:
                            results.append(_result_dict(q, "error", error=f"session_expired_and_retry_failed: {retry_err}"))
                        if 'context' in locals() and not context.is_closed():
                            await context.close()
                        continue
                else:
                    print("   Auto-login falló. Saltando cliente.")
                    for q in client_queries:
                        results.append(_result_dict(q, "error", error=f"session_expired and autologin failed"))
                    continue

            # Dump the frame HTML for debug (first time only)
            try:
                debug_html = await frame.content()
                debug_path = out_base / "_debug_consulta_form.html"
                debug_path.parent.mkdir(parents=True, exist_ok=True)
                debug_path.write_text(debug_html, encoding="utf-8")
                print(f"   Debug form HTML saved to: {debug_path}")
            except Exception:
                pass

            # Dump available inputs/buttons for debugging
            try:
                fields = await frame.evaluate(
                    "Array.from(document.querySelectorAll('input,select,button,a[href]')).map("
                    "e=>({tag:e.tagName,name:e.name||'',id:e.id||'',type:e.type||'',text:(e.innerText||e.value||'').trim().substring(0,60)}))"
                )
                print(f"   Form has {len(fields)} interactive elements")
                for f in fields[:30]:
                    print(f"      {f}")
            except Exception:
                pass

            count = 0
            for q in client_queries:
                count += 1
                if limit and count > limit:
                    break

                safe_period = (q.period or "unknown").strip() or "unknown"
                safe_book = (q.book or "cpe").strip() or "cpe"
                # Bug 3: cuando ruc_emisor está vacío (ej. boletas de venta propias),
                # usar ruc_cliente como identificador para evitar nombre "--03-EB01-XXXX"
                ruc_for_name = (q.ruc_emisor or "").strip()
                if not ruc_for_name or ruc_for_name == "-":
                    ruc_for_name = (q.ruc_cliente or "").strip() or "SIN_RUC"
                base_name = f"{ruc_for_name}-{q.tipo}-{q.serie}-{q.numero}"
                
                safe_ruc_cliente = q.ruc_cliente or "unknown_ruc"
                safe_rs_cliente = _sanitize_folder_name(q.razon_social_cliente) if q.razon_social_cliente else "Empresa"
                folder_client = f"{safe_rs_cliente} {safe_ruc_cliente}".strip()
                
                out_dir = out_base / folder_client / safe_period / safe_book
                debug_dir = out_dir / "debug"

                # Check if frame detached or reloaded
                try:
                    if frame.is_detached():
                        print("   Frame detached, re-navigating to menu...")
                        page, frame = await _navigate_to_consulta_cpe(page)
                except Exception:
                    pass

                # Skip already downloaded
                # BUGFIX: verificar XML y PDF de forma INDEPENDIENTE.
                # Si solo existe el PDF pero no el XML, NO saltar — intentar descargar el XML.
                # Solo saltar si ya existen AMBOS (o si el único que se necesita ya existe).
                if skip_existing:
                    xml_path = out_dir / "xml" / f"{base_name}.xml"
                    zip_path = out_dir / "xml" / f"{base_name}.zip"
                    pdf_path = out_dir / "pdf" / f"{base_name}.pdf"
                    
                    xml_exists = xml_path.exists() or zip_path.exists()
                    pdf_exists = pdf_path.exists()
                    
                    if prefer == "xml" and xml_exists:
                        existing_path = xml_path if xml_path.exists() else zip_path
                        results.append(_result_dict(q, "skipped", paths=[str(existing_path)]))
                        continue
                    elif prefer == "pdf" and pdf_exists:
                        results.append(_result_dict(q, "skipped", paths=[str(pdf_path)]))
                        continue
                    elif prefer == "either" and xml_exists and pdf_exists:
                        # Ambos ya descargados — saltar
                        existing_path = xml_path if xml_path.exists() else zip_path
                        results.append(_result_dict(q, "skipped", paths=[str(existing_path), str(pdf_path)]))
                        continue
                    # Si prefer=either y solo uno existe, continuar para intentar descargar el que falta

                try:
                    saved = await _search_individual(
                        page=page,
                        frame=frame,
                        query=q,
                        out_dir=out_dir,
                        base_name=base_name,
                        prefer=prefer,
                        debug_dir=debug_dir,
                        tmp_downloads_dir=tmp_downloads_dir,
                    )

                    # --- SUNAT saturado: NUNCA marcar terminal, reintentar en una corrida futura ---
                    if saved == "server_busy":
                        results.append(_result_dict(
                            q, "error",
                            error="SUNAT saturado (Error del Servidor) - se reintentará en la próxima corrida",
                        ))
                        print(f"   [server-busy] Comprobante queda PENDIENTE para reintento: {base_name}")
                        await _clear_form(frame, page=page)
                        # Pausa para darle un respiro a SUNAT antes de la siguiente consulta
                        await asyncio.sleep(8)
                        continue

                    # --- Detectar "no_descargable" para no gastar fallbacks inutilmente ---
                    if saved == "no_descargable":
                        # Detectar si estamos en formulario Hibrido (sin dropdown de tipo)
                        is_hybrid_form = not (await frame.locator("p-dropdown[formcontrolname='tipoComprobanteI']").count() > 0)
                        
                        if is_hybrid_form:
                            # En Hibrido, SUNAT busca solo por Serie/Numero.
                            # Los fallbacks repetirian la misma busqueda. Marcar como no_descargable directamente.
                            results.append(_result_dict(q, "no_descargable"))
                            print(f"   [hibrido] Comprobante sin boton de descarga (no hay dropdown de tipo, fallbacks inutiles): {base_name}")
                            await _clear_form(frame, page=page)
                            continue
                        
                        # En Angular, intentar fallbacks porque el tipo podria ser incorrecto
                        fallback_tipos = _TIPO_FALLBACKS.get(q.tipo, [])
                        if not fallback_tipos:
                            # Sin fallbacks definidos para este tipo -> marcar directamente
                            results.append(_result_dict(q, "no_descargable"))
                            print(f"   Comprobante sin boton de descarga y sin fallbacks para tipo '{q.tipo}': {base_name}")
                            await _clear_form(frame, page=page)
                            continue
                        
                        # Probar fallbacks
                        found_via_fallback = False
                        server_busy_hit = False
                        for alt_tipo in fallback_tipos:
                            print(f"   [fallback] Tipo '{q.tipo}' no descargable. Reintentando con tipo '{alt_tipo}'...")
                            await _clear_form(frame, page=page)
                            q_alt = replace(q, tipo=alt_tipo)
                            alt_base_name = f"{ruc_for_name}-{alt_tipo}-{q.serie}-{q.numero}"
                            saved = await _search_individual(
                                page=page,
                                frame=frame,
                                query=q_alt,
                                out_dir=out_dir,
                                base_name=alt_base_name,
                                prefer=prefer,
                                debug_dir=debug_dir,
                                tmp_downloads_dir=tmp_downloads_dir,
                                is_fallback=True,
                            )
                            if saved == "server_busy":
                                server_busy_hit = True
                                break  # SUNAT saturado: no seguir probando mas tipos alternativos
                            if saved and saved != "no_descargable":
                                found_via_fallback = True
                                print(f"   [fallback] Encontrado con tipo alternativo '{alt_tipo}': {alt_base_name}")
                                break
                            if saved == "no_descargable":
                                continue  # Probar siguiente tipo alternativo

                        if found_via_fallback:
                            results.append(_result_dict(q, "ok", paths=[str(p) for p in saved]))
                            print(f"Saved: {saved}")
                        elif server_busy_hit:
                            results.append(_result_dict(
                                q, "error",
                                error="SUNAT saturado (Error del Servidor) durante fallback - se reintentara",
                            ))
                            print(f"   [server-busy] Comprobante queda PENDIENTE para reintento: {base_name}")
                            await asyncio.sleep(8)
                        else:
                            results.append(_result_dict(q, "no_descargable"))
                            print(f"Comprobante encontrado pero sin descarga (todos los tipos agotados): {base_name}")

                        await _clear_form(frame, page=page)
                        continue

                    # --- Reintento con tipos alternativos si no se encontro (not_found) ---
                    if not saved:
                        fallback_tipos = _TIPO_FALLBACKS.get(q.tipo, [])
                        for alt_tipo in fallback_tipos:
                            print(f"   [fallback] Tipo '{q.tipo}' no encontrado. Reintentando con tipo '{alt_tipo}'...")
                            await _clear_form(frame, page=page)
                            q_alt = replace(q, tipo=alt_tipo)
                            alt_base_name = f"{ruc_for_name}-{alt_tipo}-{q.serie}-{q.numero}"
                            saved = await _search_individual(
                                page=page,
                                frame=frame,
                                query=q_alt,
                                out_dir=out_dir,
                                base_name=alt_base_name,
                                prefer=prefer,
                                debug_dir=debug_dir,
                                tmp_downloads_dir=tmp_downloads_dir,
                                is_fallback=True,
                            )
                            if saved == "server_busy":
                                break  # SUNAT saturado: no seguir probando mas tipos alternativos
                            if saved and saved != "no_descargable":
                                print(f"   [fallback] Encontrado con tipo alternativo '{alt_tipo}': {alt_base_name}")
                                break

                    if saved == "server_busy":
                        results.append(_result_dict(
                            q, "error",
                            error="SUNAT saturado (Error del Servidor) durante fallback - se reintentara",
                        ))
                        print(f"   [server-busy] Comprobante queda PENDIENTE para reintento: {base_name}")
                        await asyncio.sleep(8)
                    elif saved and saved != "no_descargable":
                        # Bug 4: pasar lista de paths guardados
                        results.append(_result_dict(q, "ok", paths=[str(p) for p in saved]))
                        print(f"Saved: {saved}")
                    else:
                        results.append(_result_dict(q, "not_found"))
                        print(f"Not found / no download (todos los tipos agotados): {base_name}")

                    # Clear the form for the next query
                    await _clear_form(frame, page=page)

                except Exception as e:
                    results.append(_result_dict(q, "error", error=str(e)))
                    print(f"Error: {e}")
                    # SUNAT a veces se congela o entra en bucle.
                    # Para recuperarnos, recargamos la página por completo y volvemos a abrir el menú.
                    try:
                        print("   La página parece haberse congelado. Recargando el navegador...")
                        await page.reload()
                        await asyncio.sleep(3)
                        page, frame = await _navigate_to_consulta_cpe(page)
                    except Exception as e2:
                        print(f"   Fallo al recargar la página: {e2}")
            
            # Close context for this client
            await context.close()

        await browser.close()

    return results


def _result_dict(
    q: CpeQuery,
    status: str,
    paths: list = None,
    error: str = "",
) -> dict:
    # Bug 4: normalizado a `paths` (lista) para consistencia con el orchestrator
    return {
        "status": status,
        "ruc_emisor": q.ruc_emisor,
        "tipo": q.tipo,
        "serie": q.serie,
        "numero": q.numero,
        "period": q.period,
        "book": q.book,
        "paths": paths or [],
        "error": error,
    }


# ---------------------------------------------------------------------------
# Standalone single-document mode (for manual testing)
# ---------------------------------------------------------------------------

async def run(ruc_emisor, tipo, serie, numero, importe, fecha):
    """Download a single CPE – standalone mode for testing."""
    q = CpeQuery(
        ruc_emisor=ruc_emisor,
        tipo=tipo,
        serie=serie,
        numero=numero,
        importe=importe,
        fecha=fecha,
    )
    results = await run_batch(
        [q],
        outdir=os.path.join(os.path.dirname(__file__), "downloads"),
        prefer="xml",
        headless=False,
        skip_existing=False,
        limit=0,
    )
    for r in results:
        print(r)


if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("Usage: python download_xml_scraper.py <ruc> <tipo> <serie> <num> <imp> <fecha>")
        sys.exit(1)

    asyncio.run(run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]))
