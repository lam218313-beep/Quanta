"""
SIRE PDF Downloader - Descarga PDFs de facturas desde SIRE (Compras y Ventas)

Usage:
    python sire_pdf_scraper.py [--mode compras|ventas] [--ruc RUC] [--serie SERIE] [--numero NUM]

Modes:
    compras: Descarga PDFs del Registro de Compras (facturas recibidas)
    ventas: Descarga PDFs del Registro de Ventas (facturas emitidas)
"""

import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

# Session file
SESSION_FILE = os.path.join(os.path.dirname(__file__), "sunat_session.json")


async def explore_sire_menu():
    """Explore the SIRE menu structure to find PDF download options."""
    
    if not os.path.exists(SESSION_FILE):
        print("❌ Session file not found. Run automation_scraper.py first.")
        return
    
    with open(SESSION_FILE, "r") as f:
        session_data = json.load(f)
    
    # Handle both formats: list of cookies or dict with "cookies" key
    cookies = session_data if isinstance(session_data, list) else session_data.get("cookies", [])
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible for exploration
        context = await browser.new_context()
        
        # Load cookies
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        
        print("🚀 Navigating to SUNAT Menu...")
        await page.goto("https://e-menu.sunat.gob.pe/cl-ti-itmenu/MenuInternet.htm")
        await page.wait_for_load_state("networkidle")
        
        # Handle overlays
        for selector in ["#divModalCampana", "#divModalCampanaBak"]:
            try:
                await page.evaluate(f"document.querySelector('{selector}')?.remove()")
            except:
                pass
        
        await asyncio.sleep(2)
        
        # Navigate to SIRE
        print("⏳ Navigating to SIRE...")
        
        async def click_menu_item(text):
            """Helper to click visible menu items."""
            selector = f"xpath=//*[contains(text(),'{text}')]"
            elements = await page.query_selector_all(selector)
            for el in elements:
                if await el.is_visible():
                    await el.click()
                    await asyncio.sleep(1)
                    return True
            return False
        
        # Menu path: Empresas -> Libros Electrónicos -> SIRE
        await click_menu_item("Empresas")
        await asyncio.sleep(1)
        
        await click_menu_item("Libros Electrónicos")
        await asyncio.sleep(1)
        
        # Look for SIRE options
        await click_menu_item("SIRE")
        await asyncio.sleep(1)
        
        # Explore the submenu
        print("🔎 Capturing SIRE menu structure...")
        await page.screenshot(path="debug_sire_menu.png")
        
        # Dump HTML of the page
        with open("debug_sire_menu.html", "w", encoding="utf-8") as f:
            f.write(await page.content())
        
        # List all visible menu items containing SIRE-related terms
        sire_items = await page.evaluate("""
            () => {
                const items = document.querySelectorAll('li, a, span');
                const results = [];
                for (const item of items) {
                    const text = (item.innerText || '').trim();
                    if (text.length > 0 && text.length < 100) {
                        const lower = text.toLowerCase();
                        if (lower.includes('sire') || lower.includes('compra') || 
                            lower.includes('venta') || lower.includes('registro') ||
                            lower.includes('detalle') || lower.includes('consulta')) {
                            results.push({
                                tag: item.tagName,
                                text: text.substring(0, 80),
                                visible: item.offsetParent !== null,
                                hasClick: !!item.onclick || item.hasAttribute('onclick')
                            });
                        }
                    }
                }
                return results;
            }
        """)
        
        print(f"\n📋 Found {len(sire_items)} SIRE-related menu items:")
        for item in sire_items[:30]:
            print(f"   - [{item['tag']}] {item['text']} (vis={item['visible']}, click={item['hasClick']})")
        
        print("\n📸 Screenshots saved to debug_sire_menu.png")
        print("📄 HTML saved to debug_sire_menu.html")
        
        print("\n👁️ Browser will stay open for 60 seconds for manual exploration...")
        print("   Navigate to SIRE and find where PDFs are available.")
        print("   Press Ctrl+C to close earlier.")
        
        try:
            await asyncio.sleep(60)
        except KeyboardInterrupt:
            pass
        
        await browser.close()


async def download_pdf_from_sire(mode="compras", target_ruc=None, target_serie=None, target_numero=None):
    """
    Download PDFs from SIRE module.
    
    Args:
        mode: "compras" or "ventas"
        target_ruc: Optional specific RUC to filter
        target_serie: Optional series to filter
        target_numero: Optional number to filter
    """
    
    if not os.path.exists(SESSION_FILE):
        print("❌ Session file not found. Run automation_scraper.py first.")
        return
    
    with open(SESSION_FILE, "r") as f:
        session_data = json.load(f)
    
    # Handle both formats: list of cookies or dict with "cookies" key
    cookies = session_data if isinstance(session_data, list) else session_data.get("cookies", [])
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        
        print("🚀 Navigating to SUNAT Menu...")
        await page.goto("https://e-menu.sunat.gob.pe/cl-ti-itmenu/MenuInternet.htm")
        await page.wait_for_load_state("networkidle")
        
        # Handle overlays
        for selector in ["#divModalCampana", "#divModalCampanaBak"]:
            try:
                await page.evaluate(f"document.querySelector('{selector}')?.remove()")
            except:
                pass
        
        await asyncio.sleep(2)
        
        # Navigate to SIRE
        print(f"⏳ Navigating to SIRE - Registro de {mode.capitalize()}...")
        
        async def click_visible(text, description=""):
            """Click first visible element containing text."""
            selector = f"xpath=//*[contains(text(),'{text}')]"
            elements = await page.query_selector_all(selector)
            for el in elements:
                if await el.is_visible():
                    print(f"   Clicking '{description or text}'...")
                    await el.click()
                    await asyncio.sleep(1.5)
                    return True
            print(f"   ⚠️ Could not find visible '{text}'")
            return False
        
        # Navigate menu
        await click_visible("Empresas", "Empresas")
        await click_visible("Libros Electrónicos", "Libros Electrónicos")
        await click_visible("SIRE", "SIRE")
        
        # Select Compras or Ventas
        if mode == "compras":
            await click_visible("Registro de Compras", "Registro de Compras")
        else:
            await click_visible("Registro de Ventas", "Registro de Ventas")
        
        # Look for "Consulta" or "Detalle" option
        for option in ["Consulta", "Detalle", "Ver Comprobantes", "Historial"]:
            if await click_visible(option, option):
                break
        
        await asyncio.sleep(3)
        
        # Capture current state
        await page.screenshot(path=f"debug_sire_{mode}.png")
        print(f"📸 Screenshot saved to debug_sire_{mode}.png")
        
        # Check if we landed on an iframe
        iframe_selector = "#iframeApplication"
        try:
            await page.wait_for_selector(iframe_selector, state="attached", timeout=10000)
            print("   Found iframe, switching context...")
            
            element_handle = await page.query_selector(iframe_selector)
            frame = await element_handle.content_frame()
            
            if frame:
                # Dump frame content for analysis
                with open(f"debug_sire_{mode}_frame.html", "w", encoding="utf-8") as f:
                    f.write(await frame.content())
                print(f"📄 Frame HTML saved to debug_sire_{mode}_frame.html")
                
                # Look for PDF/download buttons
                buttons = await frame.evaluate("""
                    Array.from(document.querySelectorAll('button, a, [onclick], i[class*=file], i[class*=pdf]')).map(e => ({
                        tag: e.tagName,
                        id: e.id,
                        class: e.className,
                        text: (e.innerText || e.value || '').trim().substring(0, 50),
                        title: e.title || '',
                        onclick: (e.getAttribute('onclick') || '').substring(0, 80)
                    }))
                """)
                
                print(f"\n🔎 Found {len(buttons)} buttons/links in frame:")
                for btn in buttons[:30]:
                    print(f"   - {btn}")
                
        except Exception as e:
            print(f"   No iframe found: {e}")
        
        print("\n👁️ Browser will stay open for 60 seconds for manual exploration...")
        try:
            await asyncio.sleep(60)
        except KeyboardInterrupt:
            pass
        
        await browser.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SIRE PDF Downloader")
    parser.add_argument("--explore", action="store_true", help="Explore SIRE menu structure")
    parser.add_argument("--mode", choices=["compras", "ventas"], default="compras", help="Mode: compras or ventas")
    parser.add_argument("--ruc", help="Target RUC to filter")
    parser.add_argument("--serie", help="Target series to filter")
    parser.add_argument("--numero", help="Target number to filter")
    
    args = parser.parse_args()
    
    if args.explore:
        asyncio.run(explore_sire_menu())
    else:
        asyncio.run(download_pdf_from_sire(
            mode=args.mode,
            target_ruc=args.ruc,
            target_serie=args.serie,
            target_numero=args.numero
        ))
