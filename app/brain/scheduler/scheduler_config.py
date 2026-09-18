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
    # Hour (0-23) at which the daily sync fires.  Default 6 AM.
    run_hour: int = int(os.getenv("SCHEDULER_HOUR", "6"))
    run_minute: int = int(os.getenv("SCHEDULER_MINUTE", "0"))

    # ── Pipeline steps ──────────────────────────────────────────
    # Which steps of the pipeline to run.  Set to False to skip.
    step_download_preliminar: bool = True
    step_download_xmls: bool = True
    step_generate_pdfs: bool = True
    step_enrich_xml: bool = True
    step_classify_ai: bool = True

    # ── Limits ──────────────────────────────────────────────────
    # Max XMLs to download per client per run.
    xml_download_limit: int = int(os.getenv("SCHEDULER_XML_LIMIT", "200"))
    # Max comprobantes for PDF generation per client per run.
    pdf_generation_limit: int = int(os.getenv("SCHEDULER_PDF_LIMIT", "500"))
    # Max comprobantes for enrichment per client per run.
    enrichment_limit: int = int(os.getenv("SCHEDULER_ENRICH_LIMIT", "500"))
    # Max comprobantes for AI classification per client per run.
    classification_limit: int = int(os.getenv("SCHEDULER_CLASSIFY_LIMIT", "100"))

    # ── Throttling ──────────────────────────────────────────────
    # Seconds to wait between processing different clients.
    delay_between_clients: int = int(os.getenv("SCHEDULER_CLIENT_DELAY", "15"))

    # ── Mode ────────────────────────────────────────────────────
    # "all" → process every client with credentials.
    # "list" → only process clients in `client_rucs`.
    mode: Literal["all", "list"] = "all"
    client_rucs: list[str] = field(default_factory=list)

    # ── State ───────────────────────────────────────────────────
    # Whether the scheduler is currently enabled.
    enabled: bool = False


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
