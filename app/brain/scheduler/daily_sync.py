"""
Daily Sync Pipeline — Quanta V2

Automated daily pipeline that, for every active client:
  1. Downloads the SIRE preliminar (purchases & sales TXT via API)
  2. Inserts/upserts the TXT data into the database
  3. Downloads XMLs for pending comprobantes (via API, not Playwright scraping)
  4. Generates PDFs from the downloaded XMLs (local, no SUNAT needed)
  5. Enriches comprobantes with descriptions extracted from XMLs
  6. Runs AI classification to assign accounting codes

This script can run standalone or be called by APScheduler inside FastAPI.

Usage:
    # Run once for all clients:
    python app/brain/scheduler/daily_sync.py

    # Run for a specific client:
    python app/brain/scheduler/daily_sync.py --ruc 20613022571

    # Run for a specific period (default: current month):
    python app/brain/scheduler/daily_sync.py --periodo 202609
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


async def _run_async_step(step_name: str, coro, log_lines: list[str]) -> bool:
    """
    Run an async step (like PDF generation), capture output, return True on success.
    """
    header = f"[{step_name}]"
    log_lines.append(f"\n{'─' * 50}")
    log_lines.append(f"{header} Iniciando...")

    try:
        result = await coro
        generated = result.get("generated", 0)
        errors = result.get("errors", 0)
        log_lines.append(f"{header} Generados: {generated}, Errores: {errors}")
        log_lines.append(f"{header} ✅ Completado.")
        return True
    except Exception as e:
        log_lines.append(f"{header} 💥 Excepción: {e}")
        return False


async def run_daily_sync(
    ruc: str | None = None,
    periodo: str | None = None,
) -> dict:
    """
    Execute the full daily sync pipeline for one or all clients.

    Args:
        ruc: If provided, only sync this client. Otherwise sync all clients
             with configured API credentials.
        periodo: Period to sync (YYYYMM). Defaults to current month.

    Returns:
        Summary dict with per-client results.
    """
    from app.brain.db.supabase_client import get_supabase
    from app.brain.scheduler.scheduler_config import get_scheduler_config

    config = get_scheduler_config()
    supabase = get_supabase()
    periodo = periodo or _current_periodo()
    cwd = str(_root)
    python = sys.executable

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
        f"  Fecha: {timestamp}  |  Periodo: {periodo}",
        f"  Clientes a procesar: {len(clientes)}",
        "=" * 60,
    ]

    results_by_client: dict[str, dict] = {}

    for i, cliente in enumerate(clientes, 1):
        client_ruc = cliente["ruc"]
        client_name = cliente["razon_social"]
        client_log: list[str] = []

        master_log.append(f"\n{'═' * 60}")
        master_log.append(f"  [{i}/{len(clientes)}] {client_name} ({client_ruc})")
        master_log.append(f"{'═' * 60}")

        client_result = {
            "razon_social": client_name,
            "steps": {},
        }

        # Step 1: Download SIRE Preliminar (TXT via API)
        if config.step_download_preliminar:
            ok = _run_step(
                "1-DESCARGA-PRELIMINAR",
                [python, "app/brain/sire_download_cli.py",
                 "--client", client_ruc, "--period", periodo],
                cwd, client_log,
            )
            client_result["steps"]["download_preliminar"] = "ok" if ok else "error"

        # Step 2: Download XMLs (via SIRE bot orchestrator)
        if config.step_download_xmls:
            ok = _run_step(
                "2-DESCARGA-XMLs",
                [python, "app/brain/db/sire_bot_orchestrator.py",
                 "--headless", "--limit", str(config.xml_download_limit),
                 "--ruc", client_ruc, "--periodo", periodo],
                cwd, client_log,
                timeout=config.step_timeout_seconds,
            )
            client_result["steps"]["download_xmls"] = "ok" if ok else "error"

        # Step 3: Generate PDFs from XMLs
        if config.step_generate_pdfs:
            from app.brain.services.pdf_from_xml_service import generate_pdfs_from_xmls
            ok = await _run_async_step(
                "3-GENERAR-PDFs",
                generate_pdfs_from_xmls(
                    ruc=client_ruc, periodo=periodo,
                    limit=config.pdf_generation_limit,
                ),
                client_log,
            )
            client_result["steps"]["generate_pdfs"] = "ok" if ok else "error"

        # Step 4: Enrich XMLs (extract descriptions from XML files)
        if config.step_enrich_xml:
            ok = _run_step(
                "4-ENRIQUECIMIENTO-XML",
                [python, "app/brain/db/sire_xml_enricher.py",
                 "--limit", str(config.enrichment_limit),
                 "--ruc", client_ruc, "--periodo", periodo],
                cwd, client_log,
            )
            client_result["steps"]["enrich_xml"] = "ok" if ok else "error"

        # Step 5: AI Classification
        if config.step_classify_ai:
            ok = _run_step(
                "5-CLASIFICACION-IA",
                [python, "app/brain/db/ai_classifier.py",
                 "--limit", str(config.classification_limit),
                 "--ruc", client_ruc, "--periodo", periodo],
                cwd, client_log,
            )
            client_result["steps"]["classify_ai"] = "ok" if ok else "error"

        results_by_client[client_ruc] = client_result
        master_log.extend(client_log)

        # Throttle between clients to avoid SUNAT rate limiting
        if i < len(clientes):
            master_log.append(
                f"\nEsperando {config.delay_between_clients}s antes del siguiente cliente..."
            )
            await asyncio.sleep(config.delay_between_clients)

    # ── Save summary log ─────────────────────────────────────────
    master_log.append(f"\n{'=' * 60}")
    master_log.append(f"  FIN SINCRONIZACIÓN DIARIA")
    master_log.append(f"  Clientes procesados: {len(results_by_client)}")
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
        "clientes_procesados": len(results_by_client),
        "resultados": results_by_client,
        "log_file": str(log_path),
    }


# ── CLI entry point ──────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sincronización diaria Quanta")
    parser.add_argument("--ruc", type=str, help="RUC del cliente (opcional, default: todos)")
    parser.add_argument("--periodo", type=str, help="Periodo YYYYMM (opcional, default: mes actual)")
    args = parser.parse_args()

    asyncio.run(run_daily_sync(ruc=args.ruc, periodo=args.periodo))
