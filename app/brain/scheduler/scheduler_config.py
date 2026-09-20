"""
Scheduler Configuration — Quanta V2

Centralised settings for the daily automated sync pipeline.
All values can be overridden by environment variables.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class SchedulerConfig:
    """Configuration for the daily sync scheduler."""

    # ── Schedule ────────────────────────────────────────────────
    # Hour (0-23) at which the daily sync fires.  Default 3 AM, so a full
    # run across every client has until business hours to finish.
    run_hour: int = int(os.getenv("SCHEDULER_HOUR", "3"))
    run_minute: int = int(os.getenv("SCHEDULER_MINUTE", "0"))

    # ── Pipeline steps ──────────────────────────────────────────
    # Which steps of the pipeline to run.  Set to False to skip.
    step_download_preliminar: bool = True
    step_download_xmls: bool = True
    step_generate_pdfs: bool = True
    step_enrich_xml: bool = True
    step_classify_ai: bool = True

    # ── Limits ──────────────────────────────────────────────────
    # Max XMLs to download per client per run. Kept low on purpose: at ~200
    # items a single client's step routinely blew past the 10-minute step
    # timeout (see step_timeout_seconds below), got killed mid-run, and left
    # every one of its 200 comprobantes stuck at reintentos=1 with nothing
    # downloaded. A lower per-run cap means every client makes some progress
    # every day instead of one big client starving everyone else.
    xml_download_limit: int = int(os.getenv("SCHEDULER_XML_LIMIT", "50"))
    # Max seconds subprocess.run() waits for the "2-DESCARGA-XMLs" step
    # before killing it. Must comfortably cover xml_download_limit queries
    # (each SUNAT search can take several seconds, more under load).
    step_timeout_seconds: int = int(os.getenv("SCHEDULER_STEP_TIMEOUT", "1200"))
    # Max comprobantes for PDF generation PER RUN, across ALL clients combined
    # (this step now runs once globally, not once per client - see daily_sync.py
    # Fase 2). Raised well above the old per-client value of 500 since one call
    # now has to cover everyone's backlog instead of a single client's; it's
    # cheap local rendering with no SUNAT interaction, so a high cap is safe.
    pdf_generation_limit: int = int(os.getenv("SCHEDULER_PDF_LIMIT", "3000"))
    # Max comprobantes for enrichment PER RUN, across ALL clients combined
    # (also a global step now - Fase 3). Cheap DB/regex work, same reasoning
    # as pdf_generation_limit above.
    enrichment_limit: int = int(os.getenv("SCHEDULER_ENRICH_LIMIT", "3000"))
    # Max comprobantes for AI classification PER RUN, across ALL clients
    # combined (global step - Fase 4). Deliberately NOT raised as aggressively
    # as the two limits above: each item costs a real OpenAI API call, so this
    # caps spend per run rather than just being a safety limit. Raise via
    # SCHEDULER_CLASSIFY_LIMIT if 500/run across all clients isn't enough.
    classification_limit: int = int(os.getenv("SCHEDULER_CLASSIFY_LIMIT", "500"))

    # ── Throttling ──────────────────────────────────────────────
    # Seconds to wait between processing different clients when concurrency=1.
    delay_between_clients: int = int(os.getenv("SCHEDULER_CLIENT_DELAY", "15"))
    # How many clients' full pipelines run at the same time. 1 = sequential
    # (original behaviour, safest default for the unattended nightly cron).
    # Raise this for on-demand backfill runs where waiting hours for 35
    # clients one-by-one isn't acceptable — each client gets its own
    # subprocess/browser, so this is real OS-level parallelism, not just
    # asyncio concurrency.
    concurrency: int = int(os.getenv("SCHEDULER_CONCURRENCY", "1"))

    # ── Mode ────────────────────────────────────────────────────
    # "all" → process every client with credentials.
    # "list" → only process clients in `client_rucs`.
    mode: Literal["all", "list"] = "all"
    client_rucs: list[str] = field(default_factory=list)

    # ── State ───────────────────────────────────────────────────
    # Whether the scheduler is currently enabled. Toggle via env var so it
    # can be turned off in Railway without a redeploy.
    enabled: bool = os.getenv("SCHEDULER_ENABLED", "true").lower() in ("1", "true", "yes")


# Singleton instance — importable throughout the app.
_config: SchedulerConfig | None = None


def get_scheduler_config() -> SchedulerConfig:
    """Return the shared scheduler config singleton."""
    global _config
    if _config is None:
        _config = SchedulerConfig()
    return _config


def update_scheduler_config(**kwargs) -> SchedulerConfig:
    """Update individual fields on the scheduler config."""
    cfg = get_scheduler_config()
    for k, v in kwargs.items():
        if hasattr(cfg, k):
            setattr(cfg, k, v)
    return cfg
