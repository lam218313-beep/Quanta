"""
Bot Orchestration Routes — Quanta

Kicks off and monitors the long-running SIRE scraper/automation scripts as
background subprocesses (download, login, XML enrichment, AI classification,
file sync, manual uploads, SIRE replacement upload). Migrated from the
legacy monolithic app/api.py — the subprocess/task-log machinery is kept
as module-level state here, same as the original.
"""
import os
import sys
import time
import shutil
import subprocess
import threading
import traceback
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Form, Response
from pydantic import BaseModel

from app.brain.db.supabase_client import get_supabase
from app.brain.utils.pagination import fetch_all_records
from app.brain.routes.export import ExportSireTxtRequest

router = APIRouter(prefix="/api/bot", tags=["bot"])

ROOT_DIR = Path(__file__).resolve().parents[3]
LOGS_DIR = ROOT_DIR / "app" / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Store references to running tasks to prevent overlapping
running_tasks = {}


class BotRequest(BaseModel):
    ruc: str
    periodo: str | None = None
    tipo_libro: str | None = None


def _run_sync_process(task_id: str, command: list, cwd: str):
    """Runs a command capturing stdout via PIPE (for headless/CLI processes)."""
    log_file = LOGS_DIR / f"{task_id}.log"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"[{task_id}] Starting command: {' '.join(command)}\n")
        print(f"[{task_id}] Starting command: {' '.join(command)}")

        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            # Store the actual process object so it can be killed
            if task_id in running_tasks:
                running_tasks[task_id] = process

            for line in process.stdout:
                f.write(line)
                f.flush()
                print(f"[{task_id}] {line.strip()}")

            process.wait()
            f.write(f"[{task_id}] Finished with return code {process.returncode}\n")
            print(f"[{task_id}] Finished with return code {process.returncode}")
        except Exception as e:
            err_trace = traceback.format_exc()
            f.write(f"[{task_id}] Failed to run command: {e}\n{err_trace}\n")
            print(f"[{task_id}] Failed to run command: {e}")
            print(err_trace)
        finally:
            if task_id in running_tasks:
                del running_tasks[task_id]


def _run_headed_process(task_id: str, command: list, cwd: str):
    """
    Runs a GUI/headed process (e.g. Playwright with headless=False) writing stdout
    DIRECTLY to the log file instead of via subprocess.PIPE.
    This avoids the EPIPE 'broken pipe' crash that occurs when Playwright's internal
    Node.js driver writes events back through a captured pipe.
    """
    log_file = LOGS_DIR / f"{task_id}.log"
    with open(log_file, "w", encoding="utf-8") as log_fh:
        log_fh.write(f"[{task_id}] Starting headed command: {' '.join(command)}\n")
        log_fh.flush()
        print(f"[{task_id}] Starting headed command: {' '.join(command)}")

        try:
            # Write directly to file — no PIPE, no EPIPE
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=log_fh,
                stderr=log_fh,
                text=True,
                encoding='utf-8',
                errors='replace',
                env={**os.environ, "PYTHONUNBUFFERED": "1"}  # force line-buffered output
            )
            if task_id in running_tasks:
                running_tasks[task_id] = process

            process.wait()
            log_fh.write(f"[{task_id}] Finished with return code {process.returncode}\n")
            log_fh.flush()
            print(f"[{task_id}] Headed process finished with return code {process.returncode}")
        except Exception as e:
            err_trace = traceback.format_exc()
            log_fh.write(f"[{task_id}] Failed to run headed command: {e}\n{err_trace}\n")
            log_fh.flush()
            print(f"[{task_id}] Failed to run headed command: {e}")
        finally:
            if task_id in running_tasks:
                del running_tasks[task_id]


async def run_command_in_background(task_id: str, command: list, cwd: str, headed: bool = False):
    target = _run_headed_process if headed else _run_sync_process
    thread = threading.Thread(target=target, args=(task_id, command, cwd))
    thread.daemon = True
    thread.start()


@router.get("/status")
def get_running_tasks():
    """Returns all currently running task IDs."""
    tasks = []
    for task_id, proc in running_tasks.items():
        pid = proc.pid if hasattr(proc, 'pid') else None
        tasks.append({"task_id": task_id, "pid": pid})
    return {"running_tasks": tasks, "count": len(tasks)}


@router.post("/reset")
def reset_running_tasks(task_id: str = None):
    """
    Kills and clears stuck running tasks.
    If task_id is provided, only clears that task.
    Otherwise clears ALL running tasks.
    """
    killed = []
    to_remove = [task_id] if task_id and task_id in running_tasks else list(running_tasks.keys())

    for tid in to_remove:
        proc = running_tasks.get(tid)
        if proc and hasattr(proc, 'kill'):
            try:
                proc.kill()
                killed.append(tid)
            except Exception:
                pass
        if tid in running_tasks:
            del running_tasks[tid]
            if tid not in killed:
                killed.append(tid)

    return {"cleared": killed, "message": f"Cleared {len(killed)} stuck task(s). You can now restart the bot."}


class DailySyncRequest(BaseModel):
    periodo: str | None = None  # YYYYMM, defaults to the current month
    ruc: str | None = None      # single client, or None for every client with credentials


@router.post("/run-daily-sync")
async def trigger_daily_sync(req: DailySyncRequest, background_tasks: BackgroundTasks):
    """
    Manually launches the exact same pipeline the 3am cron runs
    (app/brain/scheduler/daily_sync.py: preliminar SIRE -> descarga XML ->
    genera PDFs -> enriquecimiento -> clasificacion IA), for a period/cliente
    elegido a demanda en vez de esperar al cron. Con ~35 clientes activos y
    sin filtro de RUC esto corre secuencial y puede tomar varias horas -
    revisa el progreso con /api/bot/logs/{task_id}.
    """
    periodo = req.periodo or datetime.now().strftime("%Y%m")
    task_id = f"daily_sync_{req.ruc or 'all'}_{periodo}"
    if task_id in running_tasks:
        return {"status": "already_running", "message": "Ya hay una corrida del pipeline en curso para este periodo/cliente.", "task_id": task_id}

    cmd = [sys.executable, "app/brain/scheduler/daily_sync.py", "--periodo", periodo]
    if req.ruc:
        cmd += ["--ruc", req.ruc]

    running_tasks[task_id] = True
    background_tasks.add_task(run_command_in_background, task_id, cmd, str(ROOT_DIR))
    return {
        "status": "started",
        "message": f"Pipeline completo iniciado para {req.ruc or 'todos los clientes'} - periodo {periodo}.",
        "task_id": task_id,
    }


@router.post("/download-api")
async def trigger_download_api(req: BotRequest, background_tasks: BackgroundTasks):
    if not req.ruc or not req.periodo:
        raise HTTPException(status_code=400, detail="RUC and Periodo are required")

    task_id = f"api_{req.ruc}_{req.periodo}"
    if task_id in running_tasks:
        return {"status": "already_running", "message": "This API task is already running.", "task_id": task_id}

    cmd = [sys.executable, "app/brain/sire_download_cli.py", "--client", req.ruc, "--period", req.periodo]

    running_tasks[task_id] = True
    background_tasks.add_task(run_command_in_background, task_id, cmd, str(ROOT_DIR))
    return {"status": "started", "message": f"Started SIRE API Download for {req.ruc} - {req.periodo}", "task_id": task_id}


# ─────────────────────────────────────────────
# DESCARGA MASIVA DE PRELIMINAR SIRE (BATCH)
# ─────────────────────────────────────────────

class BatchDownloadRequest(BaseModel):
    periodo: str
    rucs: list[str] | None = None  # Si None → usa todos los clientes con credenciales


def _run_batch_download(task_id: str, rucs: list[str], periodo: str):
    """
    Worker secuencial: descarga el preliminar SIRE de cada RUC en orden,
    uno por uno. Escribe logs acumulativos en un único archivo .log.
    """
    log_file = LOGS_DIR / f"{task_id}.log"
    total = len(rucs)

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"{'='*60}\n")
        f.write(f"  INICIO DESCARGA MASIVA DE PRELIMINAR SIRE\n")
        f.write(f"  Periodo: {periodo}  |  Total clientes: {total}\n")
        f.write(f"{'='*60}\n\n")
        f.flush()

        exitosos = 0
        fallidos = 0

        for i, ruc in enumerate(rucs, 1):
            f.write(f"\n{'─'*50}\n")
            f.write(f"[PROGRESO] {i}/{total} ── Cliente RUC: {ruc}\n")
            f.write(f"{'─'*50}\n")
            f.flush()

            cmd = [
                sys.executable,
                "app/brain/sire_download_cli.py",
                "--client", ruc,
                "--period", periodo,
            ]

            try:
                process = subprocess.Popen(
                    cmd,
                    cwd=str(ROOT_DIR),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    env={**os.environ, "PYTHONUNBUFFERED": "1"},
                )

                for line in process.stdout:
                    f.write(line)
                    f.flush()

                process.wait()
                rc = process.returncode

                if rc == 0:
                    exitosos += 1
                    f.write(f"[OK] Cliente {ruc} finalizado correctamente.\n")
                else:
                    fallidos += 1
                    f.write(f"[ERROR] Cliente {ruc} terminó con código {rc}.\n")

            except Exception as e:
                fallidos += 1
                f.write(f"[EXCEPCION] Cliente {ruc}: {e}\n")

            f.flush()

            # Descanso de 15 segundos entre clientes para evitar 429 Too Many Requests de SUNAT
            if i < total:
                f.write(f"Esperando 15 segundos para no saturar a SUNAT...\n")
                f.flush()
                time.sleep(15)

        f.write(f"\n{'='*60}\n")
        f.write(f"  FIN DESCARGA MASIVA\n")
        f.write(f"  Exitosos: {exitosos}/{total}  |  Fallidos: {fallidos}/{total}\n")
        f.write(f"{'='*60}\n")
        f.flush()

    if task_id in running_tasks:
        del running_tasks[task_id]


@router.post("/batch-download-api")
async def trigger_batch_download_api(req: BatchDownloadRequest, background_tasks: BackgroundTasks):
    """
    Descarga el preliminar SIRE para múltiples clientes en cola, uno por uno.
    Si 'rucs' es None, descarga para todos los clientes que tienen usuario_sol configurado.
    """
    if not req.periodo:
        raise HTTPException(status_code=400, detail="Periodo es requerido")

    task_id = f"batch_api_{req.periodo}"
    if task_id in running_tasks:
        return {
            "status": "already_running",
            "message": "Ya hay una descarga masiva en curso para este periodo.",
            "task_id": task_id,
        }

    # Determinar la lista de RUCs a procesar
    rucs_to_process = req.rucs
    if not rucs_to_process:
        # Obtener todos los clientes con credenciales SOL y API configuradas
        sb = get_supabase()
        res = sb.table("clientes").select("ruc, usuario_sol, clave_sol, client_id_api, client_secret_api").execute()
        clientes_data = res.data or []
        rucs_to_process = [
            c["ruc"]
            for c in clientes_data
            if c.get("usuario_sol") and c.get("clave_sol") and c.get("client_id_api") and c.get("client_secret_api")
        ]

    if not rucs_to_process:
        raise HTTPException(
            status_code=400,
            detail="No hay clientes con credenciales SOL configuradas para procesar.",
        )

    running_tasks[task_id] = True
    background_tasks.add_task(_run_batch_download, task_id, rucs_to_process, req.periodo)

    return {
        "status": "started",
        "message": f"Descarga masiva iniciada: {len(rucs_to_process)} clientes para el periodo {req.periodo}.",
        "task_id": task_id,
        "total_clientes": len(rucs_to_process),
    }


@router.post("/automation-login")
async def trigger_automation_login(req: BotRequest, background_tasks: BackgroundTasks):
    if not req.ruc:
        raise HTTPException(status_code=400, detail="RUC is required")

    task_id = f"login_{req.ruc}"
    if task_id in running_tasks:
        return {"status": "already_running", "message": "Login task is already running.", "task_id": task_id}

    cmd = [sys.executable, "-u", "app/brain/automation_scraper.py", "--ruc", req.ruc]

    running_tasks[task_id] = True
    # Use headed=True to avoid EPIPE crash with Playwright's headed browser
    background_tasks.add_task(run_command_in_background, task_id, cmd, str(ROOT_DIR), True)
    return {"status": "started", "message": f"Started Authentication bot for {req.ruc}", "task_id": task_id}


@router.post("/download-fisicos")
async def trigger_download_fisicos(req: BotRequest, background_tasks: BackgroundTasks):
    if not req.ruc:
        raise HTTPException(status_code=400, detail="RUC is required")

    task_id = f"fisicos_{req.ruc}"
    if req.tipo_libro:
        task_id += f"_{req.tipo_libro}"

    if task_id in running_tasks:
        return {"status": "already_running", "message": "XML Scraper is already running.", "task_id": task_id}

    cmd = [sys.executable, "app/brain/db/sire_bot_orchestrator.py", "--headless", "--limit", "200", "--ruc", req.ruc]
    if req.periodo:
        cmd += ["--periodo", req.periodo]
    if req.tipo_libro:
        cmd += ["--tipo_libro", req.tipo_libro]

    running_tasks[task_id] = True
    background_tasks.add_task(run_command_in_background, task_id, cmd, str(ROOT_DIR))

    msg_suffix = f" - {req.periodo or 'todos los periodos'}"
    if req.tipo_libro:
        msg_suffix += f" (Solo {req.tipo_libro})"

    return {"status": "started", "message": f"Started XML Download bot for {req.ruc}{msg_suffix}", "task_id": task_id}


@router.post("/sync-files")
async def trigger_sync_files(background_tasks: BackgroundTasks):
    """Scans all local download folders and reconciles with Supabase DB."""
    task_id = "sync_files"
    if task_id in running_tasks:
        return {"status": "already_running", "message": "Sync is already running.", "task_id": task_id}

    cmd = [sys.executable, "app/brain/db/sync_files.py"]

    running_tasks[task_id] = True
    background_tasks.add_task(run_command_in_background, task_id, cmd, str(ROOT_DIR))
    return {"status": "started", "message": "Sincronizando archivos físicos con base de datos...", "task_id": task_id}


@router.get("/local-files")
def get_local_files():
    """Devuelve una lista plana de todos los nombres de archivo (.xml, .pdf, .zip) en la carpeta local downloads."""
    downloads_dir = ROOT_DIR / "downloads"

    if not downloads_dir.exists():
        return {"files": []}

    files = []
    try:
        # Escaneo ultra rápido de la carpeta de descargas
        for f in downloads_dir.rglob("*.*"):
            if f.suffix.lower() in ('.xml', '.pdf', '.zip'):
                files.append(f.name)
    except Exception:
        pass

    return {"files": list(set(files))}


@router.post("/upload-manual")
async def upload_manual_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    ruc_tercero: str = Form(...),
    tipo_cp: str = Form(...),
    serie: str = Form(...),
    numero: str = Form(...),
    cliente_ruc: str = Form(...)
):
    try:
        downloads_dir = ROOT_DIR / "downloads" / "manual_uploads"
        downloads_dir.mkdir(parents=True, exist_ok=True)

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.xml', '.zip', '.pdf']:
            raise HTTPException(status_code=400, detail="El archivo debe ser .xml, .zip o .pdf")

        ruc_terc = ruc_tercero.strip()
        if not ruc_terc or ruc_terc == '-':
            ruc_terc = cliente_ruc

        filename = f"{ruc_terc}-{tipo_cp}-{serie}-{numero}{ext}"
        filepath = downloads_dir / filename

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Ejecutar sync_files para actualizar la base de datos
        cmd = [sys.executable, "app/brain/db/sync_files.py"]
        background_tasks.add_task(run_command_in_background, f"sync_manual_{time.time()}", cmd, str(ROOT_DIR))

        return {"status": "ok", "message": "Archivo subido y sincronización iniciada", "filename": filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enrich-xml")
async def trigger_enrich_xml(req: BotRequest, background_tasks: BackgroundTasks):
    if not req.ruc:
        raise HTTPException(status_code=400, detail="RUC is required")

    task_id = f"enrich_{req.ruc}"
    if task_id in running_tasks:
        return {"status": "already_running", "message": "XML Enricher is already running.", "task_id": task_id}

    cmd = [sys.executable, "app/brain/db/sire_xml_enricher.py", "--limit", "500", "--ruc", req.ruc]
    if req.periodo:
        cmd += ["--periodo", req.periodo]

    running_tasks[task_id] = True
    background_tasks.add_task(run_command_in_background, task_id, cmd, str(ROOT_DIR))
    return {"status": "started", "message": f"Started XML Extraction bot for {req.ruc} - {req.periodo or 'todos los periodos'}", "task_id": task_id}


@router.post("/classify-ai")
async def trigger_classify_ai(req: BotRequest, background_tasks: BackgroundTasks):
    if not req.ruc:
        raise HTTPException(status_code=400, detail="RUC is required")

    task_id = f"classify_{req.ruc}"
    if task_id in running_tasks:
        return {"status": "already_running", "message": "AI Classifier is already running.", "task_id": task_id}

    cmd = [sys.executable, "app/brain/db/ai_classifier.py", "--limit", "100", "--ruc", req.ruc]
    if req.periodo:
        cmd += ["--periodo", req.periodo]

    running_tasks[task_id] = True
    background_tasks.add_task(run_command_in_background, task_id, cmd, str(ROOT_DIR))
    return {"status": "started", "message": f"Started AI Classifier bot for {req.ruc} - {req.periodo or 'todos los periodos'}", "task_id": task_id}


@router.get("/logs/{task_id}")
def get_task_logs(task_id: str):
    log_file = LOGS_DIR / f"{task_id}.log"
    is_running = task_id in running_tasks
    if not log_file.exists():
        return {"task_id": task_id, "logs": "No logs available yet...", "is_running": is_running}

    with open(log_file, "r", encoding="utf-8", errors="replace") as f:
        # For huge files, we should probably read the last N lines, but for these bots it should be fine.
        content = f.read()

    return {"task_id": task_id, "logs": content, "is_running": is_running}


@router.get("/comprobante-file/{fisico_id}")
def download_comprobante_file(fisico_id: str, tipo: str):
    """Sirve el XML o PDF de un comprobante físico desde Supabase Storage.

    El disco local de Railway es efímero (se borra en cada deploy), así que
    sire_bot_orchestrator.py sube cada archivo al bucket 'comprobantes-fisicos'
    apenas se descarga y guarda esa ruta de Storage en ruta_xml/ruta_pdf.
    """
    if tipo not in ("xml", "pdf"):
        raise HTTPException(status_code=400, detail="tipo debe ser 'xml' o 'pdf'")

    supabase = get_supabase()
    res = supabase.table("sire_comprobantes_fisicos") \
        .select("ruta_xml, ruta_pdf, serie, numero") \
        .eq("id", fisico_id).limit(1).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Comprobante no encontrado")

    row = res.data[0]
    ruta = row.get("ruta_xml") if tipo == "xml" else row.get("ruta_pdf")
    if not ruta:
        raise HTTPException(status_code=404, detail="El archivo aún no está disponible para este comprobante")

    suffix = Path(ruta).suffix.lower()
    try:
        content = supabase.storage.from_("comprobantes-fisicos").download(ruta)
    except Exception:
        raise HTTPException(status_code=404, detail="El archivo ya no existe en Supabase Storage")

    media_type = "application/zip" if suffix == ".zip" else (
        "application/pdf" if tipo == "pdf" else "application/xml"
    )
    filename = f"{row.get('serie') or ''}-{row.get('numero') or ''}{suffix}"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/sync-files")
def sync_files_api():
    try:
        # Run sync_files.py synchronously and capture output
        cmd = [sys.executable, "app/brain/db/sync_files.py"]
        result = subprocess.run(cmd, cwd=str(ROOT_DIR), capture_output=True, text=True, encoding='utf-8')
        return {"status": "ok", "message": "Archivos sincronizados", "output": result.stdout}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/upload-sire")
async def bot_upload_sire(req: ExportSireTxtRequest, background_tasks: BackgroundTasks):
    """
    Genera el TXT de reemplazo para SIRE, lo comprime en ZIP y llama al bot
    para subirlo a SUNAT en segundo plano.
    """
    from app.brain.db.sire_txt_exporter import build_sire_compras_txt, build_sire_ventas_txt
    import zipfile
    import tempfile

    supabase = get_supabase()

    res_cli = supabase.table("clientes").select("*").eq("ruc", req.ruc).execute()
    if not res_cli.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente = res_cli.data[0]

    # 1. Generar TXT
    if req.tipo_libro == "COMPRAS":
        res = fetch_all_records("sire_preliminar_compras", supabase, "*", {"cliente_id": cliente["id"], "periodo": req.periodo}, "fecha_emision")
        txt_content = build_sire_compras_txt(res.data, req.ruc, req.periodo)
        filename_txt = f"LE{req.ruc}{req.periodo}000804000211112.txt"
    else:
        res = fetch_all_records("sire_preliminar_ventas", supabase, "*", {"cliente_id": cliente["id"], "periodo": req.periodo}, "fecha_emision")
        txt_content = build_sire_ventas_txt(res.data, req.ruc, req.periodo)
        filename_txt = f"LE{req.ruc}{req.periodo}001404000211112.txt"

    # 2. Guardar TXT y comprimir en ZIP
    tmp_dir = tempfile.gettempdir()
    zip_path = os.path.join(tmp_dir, filename_txt.replace(".txt", ".zip"))
    txt_path = os.path.join(tmp_dir, filename_txt)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt_content)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(txt_path, arcname=filename_txt)

    # 3. Llamar a la API de SIRE en background
    def run_sire_upload_api():
        from app.brain.integrations.sunat_sire import SunatSireClient

        print(f"Subiendo a SUNAT SIRE vía API para {req.ruc} - {req.periodo} ({req.tipo_libro})...")
        try:
            # Obtener credenciales (de BD o de entorno como fallback)
            client_id = cliente.get("api_client_id") or os.getenv("SUNAT_CLIENT_ID")
            client_secret = cliente.get("api_client_secret") or os.getenv("SUNAT_CLIENT_SECRET")
            ruc = cliente.get("ruc") or os.getenv("SUNAT_RUC")
            sol_user = cliente.get("sol_user") or os.getenv("SUNAT_USERNAME")
            sol_pass = cliente.get("sol_pass") or os.getenv("SUNAT_PASSWORD")

            if not client_id or not client_secret:
                print("Error: No hay credenciales API (client_id/client_secret) configuradas.")
                return

            client = SunatSireClient(
                client_id=client_id,
                client_secret=client_secret,
                ruc=ruc,
                username=sol_user,
                password=sol_pass
            )

            book_type = "sales" if req.tipo_libro == "VENTAS" else "purchases"

            ticket_id = client.upload_replacement(
                period=req.periodo,
                book_type=book_type,
                zip_path=zip_path
            )
            print(f"=== ÉXITO: PROPUESTA REEMPLAZADA ===")
            print(f"Ticket generado por SUNAT: {ticket_id}")

        except Exception as e:
            print(f"Error subiendo a la API de SUNAT: {e}")

    background_tasks.add_task(run_sire_upload_api)

    return {"ok": True, "message": "Bot de subida a SUNAT iniciado en segundo plano", "zip_path": zip_path}
