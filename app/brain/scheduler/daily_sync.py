"""
Daily Sync Pipeline — Quanta V2

Automated daily pipeline that, for every active client:
  1. Downloads the SIRE preliminar (purchases & sales TXT via API)
  2. Inserts/upserts the TXT data into the database
  3. Downloads XMLs for pending comprobantes (via API, not Playwright scraping)
  4. Generates PDFs from the downloaded XMLs (local, no SUNAT needed)
  5. Enriches comprobantes with descriptions extracted from XMLs
  6. Runs AI classification to assign accounting codes

Clients are processed with bounded concurrency (default 1, i.e. sequential —
same as before). Each client's full 5-step pipeline runs in its own worker
thread so multiple clients' subprocesses/Playwright sessions can be in
flight at once without one client's SUNAT wait blocking every other client.

This script can run standalone or be called by APScheduler inside FastAPI.

Usage:
    # Run once for all clients:
    python app/brain/scheduler/daily_sync.py

    # Run for a specific client:
    python app/brain/scheduler/daily_sync.py --ruc 20613022571

    # Run for a specific period (default: current month):
    python app/brain/scheduler/daily_sync.py --periodo 202609

    # Run up to 5 clients in parallel:
    python app/brain/scheduler/daily_sync.py --periodo 202608 --concurrency 5
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Ensure we can import app modules
_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


def _current_periodo() -> str:
    """Return current month as YYYYMM string."""
    return datetime.now().strftime("%Y%m")


def _run_step(step_name: str, cmd: list[str], cwd: str, log_lines: list[str], timeout: int = 600) -> bool:
    """
    Run a subprocess step, capture output, and return True on success.
    """
    header = f"[{step_name}]"
    log_lines.append(f"\n{'─' * 50}")
    log_lines.append(f"{header} Iniciando...")
    log_lines.append(f"{header} Comando: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )

        # Capture last 20 lines of output for the summary log
        output_lines = (result.stdout or "").strip().split("\n")
        tail = output_lines[-20:] if len(output_lines) > 20 else output_lines
        for line in tail:
            log_lines.append(f"  {line}")

        if result.returncode == 0:
            log_lines.append(f"{header} ✅ Completado exitosamente.")
            return True
        else:
            log_lines.append(f"{header} ❌ Falló con código {result.returncode}")
            if result.stderr:
                for line in result.stderr.strip().split("\n")[-5:]:
                    log_lines.append(f"  [STDERR] {line}")
            return False

    except subprocess.TimeoutExpired:
        log_lines.append(f"{header} ⏰ Timeout ({timeout}s) excedido.")
        return False
    except Exception as e:
        log_lines.append(f"{header} 💥 Excepción: {e}")
        return False


def _count_descargados(supabase, cliente_id: str, periodo: str) -> Optional[int]:
    """Cuenta XMLs en estado DESCARGADO para un cliente+periodo. None si la query falla."""
    try:
        res = (
            supabase.table("sire_comprobantes_fisicos")
            .select("id", count="exact")
            .eq("cliente_id", cliente_id)
            .eq("periodo", periodo)
            .eq("estado_xml", "DESCARGADO")
            .execute()
        )
        return res.count or 0
    except Exception:
        return None


def _process_client_sync(
    cliente: dict,
    periodo: str,
    config,
    cwd: str,
    python: str,
    index: int,
    total: int,
) -> tuple[str, dict, list[str]]:
    """
    Runs all 5 pipeline steps for a single client, synchronously, measuring
    the duration of every step. Designed to run inside a worker thread
    (via asyncio.to_thread) so several clients can be processed at once.
    """
    from app.brain.db.supabase_client import get_supabase

    client_ruc = cliente["ruc"]
    client_name = cliente["razon_social"]
    client_log: list[str] = [
        f"\n{'═' * 60}",
        f"  [{index}/{total}] {client_name} ({client_ruc})",
        f"{'═' * 60}",
    ]
    client_result: dict = {"razon_social": client_name, "steps": {}}
    client_start = time.monotonic()
    supabase = get_supabase()

    def _record(step_key: str, step_label: str, ok: bool, t0: float, extra: str = "") -> None:
        dur = round(time.monotonic() - t0, 1)
        client_result["steps"][step_key] = {"status": "ok" if ok else "error", "duration_seconds": dur}
        client_log.append(f"[timing] {step_label}: {dur}s{extra}")

    # Step 1: Download SIRE Preliminar (TXT via API)
    if config.step_download_preliminar:
        t0 = time.monotonic()
        ok = _run_step(
            "1-DESCARGA-PRELIMINAR",
            [python, "app/brain/sire_download_cli.py", "--client", client_ruc, "--period", periodo],
            cwd, client_log,
        )
        _record("download_preliminar", "1-DESCARGA-PRELIMINAR", ok, t0)

    # Step 2: Download XMLs (via SIRE bot orchestrator) — measure real throughput
    # via a before/after DB count, not just pass/fail.
    if config.step_download_xmls:
        before = _count_descargados(supabase, cliente["id"], periodo)
        t0 = time.monotonic()
        ok = _run_step(
            "2-DESCARGA-XMLs",
            [python, "app/brain/db/sire_bot_orchestrator.py",
             "--headless", "--limit", str(config.xml_download_limit),
             "--ruc", client_ruc, "--periodo", periodo],
            cwd, client_log,
            timeout=config.step_timeout_seconds,
        )
        after = _count_descargados(supabase, cliente["id"], periodo)
        delta = (after - before) if (before is not None and after is not None) else None
        client_result["xml_downloaded_delta"] = delta
        _record(
            "download_xmls", "2-DESCARGA-XMLs", ok, t0,
            extra=f" (XML descargados: +{delta})" if delta is not None else "",
        )

    # Step 3: Generate PDFs from XMLs. Own asyncio loop — this runs inside a
    # worker thread with no loop of its own, so asyncio.run() here is safe
    # and does not interfere with the caller's event loop.
    if config.step_generate_pdfs:
        from app.brain.services.pdf_from_xml_service import generate_pdfs_from_xmls
        t0 = time.monotonic()
        try:
            result = asyncio.run(
                generate_pdfs_from_xmls(ruc=client_ruc, periodo=periodo, limit=config.pdf_generation_limit)
            )
            client_log.append(
                f"[3-GENERAR-PDFs] Generados: {result.get('generated', 0)}, Errores: {result.get('errors', 0)}"
            )
            ok = True
        except Exception as e:
            client_log.append(f"[3-GENERAR-PDFs] 💥 Excepción: {e}")
            ok = False
        _record("generate_pdfs", "3-GENERAR-PDFs", ok, t0)

    # Step 4: Enrich XMLs (extract descriptions from XML files)
    if config.step_enrich_xml:
        t0 = time.monotonic()
        ok = _run_step(
            "4-ENRIQUECIMIENTO-XML",
            [python, "app/brain/db/sire_xml_enricher.py",
             "--limit", str(config.enrichment_limit), "--ruc", client_ruc, "--periodo", periodo],
            cwd, client_log,
        )
        _record("enrich_xml", "4-ENRIQUECIMIENTO-XML", ok, t0)

    # Step 5: AI Classification
    if config.step_classify_ai:
        t0 = time.monotonic()
        ok = _run_step(
            "5-CLASIFICACION-IA",
            [python, "app/brain/db/ai_classifier.py",
             "--limit", str(config.classification_limit), "--ruc", client_ruc, "--periodo", periodo],
            cwd, client_log,
        )
        _record("classify_ai", "5-CLASIFICACION-IA", ok, t0)

    total_dur = round(time.monotonic() - client_start, 1)
    client_result["duration_seconds"] = total_dur
    client_log.append(f"[timing] TOTAL cliente {client_ruc}: {total_dur}s ({total_dur / 60:.1f} min)")

    return client_ruc, client_result, client_log


async def run_daily_sync(
    ruc: str | None = None,
    periodo: str | None = None,
    concurrency: int | None = None,
) -> dict:
    """
    Execute the full daily sync pipeline for one or all clients.

    Args:
        ruc: If provided, only sync this client. Otherwise sync all clients
             with configured API credentials.
        periodo: Period to sync (YYYYMM). Defaults to current month.
        concurrency: Max number of clients processed at the same time.
             Defaults to config.concurrency (1 = sequential, same as before).

    Returns:
        Summary dict with per-client results and timing.
    """
    from app.brain.db.supabase_client import get_supabase
    from app.brain.scheduler.scheduler_config import get_scheduler_config

    config = get_scheduler_config()
    supabase = get_supabase()
    periodo = periodo or _current_periodo()
    cwd = str(_root)
    python = sys.executable
    concurrency = max(1, concurrency or config.concurrency)
    # Stagger initial logins within a concurrent wave so N clients don't all
    # hit SUNAT in the same instant. Sequential mode keeps the original
    # inter-client throttle unchanged.
    stagger_seconds = config.delay_between_clients if concurrency == 1 else 3

    # ── Determine which clients to process ───────────────────────
    if ruc:
        clientes_query = supabase.table("clientes").select(
            "id, ruc, razon_social, usuario_sol, clave_sol, client_id_api, client_secret_api"
        ).eq("ruc", ruc).eq("activo", True).execute()
    else:
        clientes_query = supabase.table("clientes").select(
            "id, ruc, razon_social, usuario_sol, clave_sol, client_id_api, client_secret_api"
        ).eq("activo", True).execute()

    clientes = [
        c for c in (clientes_query.data or [])
        if c.get("usuario_sol") and c.get("clave_sol")
           and c.get("client_id_api") and c.get("client_secret_api")
    ]

    if config.mode == "list" and config.client_rucs:
        clientes = [c for c in clientes if c["ruc"] in config.client_rucs]

    if not clientes:
        return {"error": "No hay clientes con credenciales completas para procesar."}

    # ── Run pipeline ─────────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    master_log: list[str] = [
        "=" * 60,
        f"  SINCRONIZACIÓN DIARIA QUANTA",
        f"  Fecha: {timestamp}  |  Periodo: {periodo}  |  Concurrencia: {concurrency}",
        f"  Clientes a procesar: {len(clientes)}",
        "=" * 60,
    ]

    run_start = time.monotonic()
    semaphore = asyncio.Semaphore(concurrency)

    async def _run_one(cliente: dict, idx: int):
        stagger = ((idx - 1) % concurrency) * stagger_seconds
        if stagger:
            await asyncio.sleep(stagger)
        async with semaphore:
            return await asyncio.to_thread(
                _process_client_sync, cliente, periodo, config, cwd, python, idx, len(clientes)
            )

    tasks = [_run_one(c, i) for i, c in enumerate(clientes, 1)]
    completed = await asyncio.gather(*tasks, return_exceptions=True)

    results_by_client: dict[str, dict] = {}
    total_xml_delta = 0
    for res in completed:
        if isinstance(res, Exception):
            master_log.append(f"\n[ERROR] Excepción no controlada procesando un cliente: {res}")
            continue
        client_ruc, client_result, client_log = res
        results_by_client[client_ruc] = client_result
        master_log.extend(client_log)
        delta = client_result.get("xml_downloaded_delta")
        if delta:
            total_xml_delta += delta

    run_duration = round(time.monotonic() - run_start, 1)

    # ── Save summary log ─────────────────────────────────────────
    master_log.append(f"\n{'=' * 60}")
    master_log.append(f"  FIN SINCRONIZACIÓN DIARIA")
    master_log.append(f"  Clientes procesados: {len(results_by_client)}  |  Concurrencia: {concurrency}")
    master_log.append(f"  Duración total: {run_duration}s ({run_duration / 60:.1f} min)")
    master_log.append(f"  XML descargados en esta corrida: {total_xml_delta}")
    if run_duration > 0 and total_xml_delta:
        master_log.append(f"  Throughput: {total_xml_delta / (run_duration / 60):.2f} XML/min")
    master_log.append(f"{'=' * 60}")

    log_dir = _root / "app" / "logs"
    log_dir.mkdir(exist_ok=True)
    log_filename = f"daily_sync_{periodo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = log_dir / log_filename

    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(master_log))

    print("\n".join(master_log))

    return {
        "periodo": periodo,
        "concurrency": concurrency,
        "clientes_procesados": len(results_by_client),
        "duracion_segundos": run_duration,
        "xml_descargados": total_xml_delta,
        "resultados": results_by_client,
        "log_file": str(log_path),
    }


# ── CLI entry point ──────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sincronización diaria Quanta")
    parser.add_argument("--ruc", type=str, help="RUC del cliente (opcional, default: todos)")
    parser.add_argument("--periodo", type=str, help="Periodo YYYYMM (opcional, default: mes actual)")
    parser.add_argument("--concurrency", type=int, help="Clientes en paralelo (opcional, default: 1)")
    args = parser.parse_args()

    asyncio.run(run_daily_sync(ruc=args.ruc, periodo=args.periodo, concurrency=args.concurrency))
