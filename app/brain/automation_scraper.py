import asyncio
from playwright.async_api import async_playwright
import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]

def _ensure_import_path() -> None:
    root = str(_repo_root())
    if root not in sys.path:
        sys.path.insert(0, root)

# Load Env
load_dotenv(_repo_root() / '.env')

SUNAT_LOGIN_URL = "https://e-menu.sunat.gob.pe/cl-ti-itmenu/MenuInternet.htm"

import argparse

async def run(ruc: str):
    async with async_playwright() as p:
        # Launch browser in HEADLESS mode for Railway compatibility
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()

        print(f"🚀 Opening SUNAT Login Page for RUC {ruc}...")
        await page.goto(SUNAT_LOGIN_URL)
        await page.wait_for_load_state('domcontentloaded')
        
        # Intentar autocompletado si hay credenciales
        _ensure_import_path()
        from app.brain.db.supabase_client import get_supabase
        supabase = get_supabase()
        resp = supabase.table("clientes").select("usuario_sol, clave_sol").eq("ruc", ruc).execute()
        
        if resp.data and resp.data[0].get("usuario_sol") and resp.data[0].get("clave_sol"):
            print("🔑 Credentials found in database! Auto-filling form...")
            try:
                usuario = resp.data[0]["usuario_sol"]
                clave = resp.data[0]["clave_sol"]
                
                await page.fill("#txtRuc", ruc)
                await page.fill("#txtUsuario", usuario)
                await page.fill("#txtContrasena", clave)
                await page.click("#btnAceptar")
                print("   Login button clicked. Waiting for response...")
            except Exception as e:
                print(f"   Auto-fill failed: {e}. Please log in manually.")
        else:
            print("👤 No credentials found. Please Log In manually in the browser window.")

        print("⏳ Checking login status...")
        
        # In headless mode (Railway/Production), we cannot wait for a user to click.
        # We just wait for the login to redirect to the Menu URL, and save the base cookies.
        try:
            try:
                # 8s (era 5s): Railway renderiza el login mas lento que un equipo
                # local, por latencia de red hacia SUNAT y menos CPU disponible.
                await page.wait_for_url("**/MenuInternet.htm*", timeout=8000)
                print("✅ Login successful! Redirected to menu.")
                found_session = True
            except Exception:
                if await page.locator("#btnWithOutCode").count() > 0:
                    print("   [Workaround] Authentication screen detected. Clicking 'Continuar sin código'...")
                    await page.click("#btnWithOutCode")

                # 30s (era 15s): mismo margen que arriba, para el mismo motivo.
                await page.wait_for_url("**/MenuInternet.htm*", timeout=30000)
                print("✅ Login successful! Redirected to menu.")
                found_session = True
        except Exception as e:
            print(f"⚠️ Did not reach menu URL in time, or CAPTCHA required: {e}")
            found_session = False

            # DIAGNOSTICO TEMPORAL: capturar que le muestra SUNAT a esta IP en
            # el momento exacto del timeout (screenshot + HTML), subido a
            # Storage para poder revisarlo fuera de Railway. Quitar una vez
            # diagnosticado el problema real detras de este timeout.
            try:
                import time
                ts = int(time.time())
                screenshot_bytes = await page.screenshot(full_page=True)
                html = await page.content()
                current_url = page.url
                print(f"   [DIAG] URL en el momento del timeout: {current_url}")

                _ensure_import_path()
                from app.brain.db.supabase_client import get_supabase
                diag_supabase = get_supabase()
                png_path = f"_diagnostics/{ruc}_{ts}.png"
                html_path = f"_diagnostics/{ruc}_{ts}.html"
                diag_supabase.storage.from_("comprobantes-fisicos").upload(
                    path=png_path, file=screenshot_bytes,
                    file_options={"content-type": "image/png", "upsert": "true"},
                )
                diag_supabase.storage.from_("comprobantes-fisicos").upload(
                    path=html_path, file=html.encode("utf-8"),
                    file_options={"content-type": "text/html", "upsert": "true"},
                )
                print(f"   [DIAG] Screenshot subido a: {png_path}")
                print(f"   [DIAG] HTML subido a: {html_path}")
            except Exception as diag_err:
                print(f"   [DIAG] No se pudo capturar diagnostico: {diag_err}")

        try:
            # Extract Cookies Final
            cookies = await context.cookies()
            
            if found_session or len(cookies) > 5:
                print(f"🎉 Success! Extracted {len(cookies)} cookies.")
                
                # Save cookies to a file based on RUC
                cookie_file = os.path.join(os.path.dirname(__file__), f"sunat_session_{ruc}.json")
                with open(cookie_file, "w") as f:
                    json.dump(cookies, f, indent=2)
                
                print(f"💾 Session saved to: {cookie_file}")
            else:
                print("❌ Timeout: Did not detect session cookies after 5 minutes.")
        except Exception as e:
            print(f"❌ Error during scrape: {e}")
        
        print("👋 Closing browser...")
        await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SUNAT Manual Login")
    parser.add_argument("--ruc", required=True, help="RUC of the client you are logging into")
    args = parser.parse_args()
    
    asyncio.run(run(args.ruc))
