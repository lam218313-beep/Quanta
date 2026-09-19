"""
Contax Brain API - Main Entry Point
The AI Orchestration Layer for Peruvian Accounting Automation

Run with:  uvicorn app.api:app --reload --port 8000  (from the project root)
"""
import subprocess
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

# The route modules in app/brain/routes use two different import conventions:
#   - absolute, e.g. `from app.brain.db.supabase_client import get_supabase`  (users, dashboard, pdf, auth)
#   - bare/relative to app/brain, e.g. `from db.supabase_client import get_supabase`  (documents, linking, analytics, sire)
# Registering both the project root and app/brain on sys.path lets every module
# resolve its imports without rewriting them file by file.
_ROOT = Path(__file__).resolve().parent.parent
_BRAIN = _ROOT / "app" / "brain"
for _path in (str(_ROOT), str(_BRAIN)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Two separate .env files exist in this project: the root one (AI provider keys)
# and app/.env (Supabase, Odoo, SUNAT, encryption — everything the backend needs).
# Plain `load_dotenv()` only finds the first one by cwd auto-discovery, silently
# leaving ENCRYPTION_KEY etc. unset, so both are loaded explicitly here.
load_dotenv(_ROOT / ".env")
load_dotenv(_BRAIN.parent / ".env")

from app.brain.db.supabase_client import get_supabase
from app.brain.db.odoo_client import get_odoo

from app.brain.routes.documents import router as documents_router
from app.brain.routes.linking import router as linking_router
from app.brain.routes.analytics import router as analytics_router
from app.brain.routes.pdf import router as pdf_router
from app.brain.routes.sire import router as sire_router, credentials_router as sire_credentials_router
from app.brain.routes.dashboard import router as dashboard_router
from app.brain.routes.users import router as users_router
from app.brain.routes.export import router as export_router
from app.brain.routes.bot import router as bot_router
from app.brain.routes.facturacion import router as facturacion_router
from app.brain.routes.processing import router as processing_router
from app.brain.routes.client_auth import router as client_auth_router
from app.brain.scheduler.scheduler_config import get_scheduler_config


def _launch_daily_sync():
    """Fire-and-forget subprocess launch for the scheduled daily sync.

    Runs as its own process (like every other bot task in bot.py) instead of
    calling run_daily_sync() in-process — that pipeline can take hours across
    every client, and awaiting it here would block the API's event loop for
    the whole run, including health checks.
    """
    log_dir = _ROOT / "app" / "logs"
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / f"daily_sync_scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_fh = open(log_path, "w", encoding="utf-8")
    subprocess.Popen(
        [sys.executable, "app/brain/scheduler/daily_sync.py"],
        cwd=str(_ROOT),
        stdout=log_fh,
        stderr=log_fh,
    )
    log_fh.close()
    print(f"[scheduler] Daily sync launched, logging to {log_path}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = None
    config = get_scheduler_config()
    if config.enabled:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger

        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            _launch_daily_sync,
            trigger=CronTrigger(hour=config.run_hour, minute=config.run_minute),
            id="daily_sync",
        )
        scheduler.start()
        print(f"[scheduler] Daily sync cron active — fires at {config.run_hour:02d}:{config.run_minute:02d} daily.")
    else:
        print("[scheduler] Daily sync cron disabled (SCHEDULER_ENABLED=false).")

    yield

    if scheduler:
        scheduler.shutdown(wait=False)


# Initialize FastAPI app
app = FastAPI(
    title="Contax Brain API",
    description="AI-powered accounting automation for Peru",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS Configuration (for Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    # Vercel gives every deploy (production + each preview) its own unique
    # subdomain, and can reassign the production alias to a different short
    # name too (e.g. quanta-app-chi.vercel.app) — match anything under this
    # project's naming instead of hardcoding one URL that changes on deploy.
    allow_origin_regex=r"https://quanta[\w-]*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Include routers
app.include_router(documents_router)
app.include_router(linking_router)
app.include_router(analytics_router)
app.include_router(pdf_router)
app.include_router(sire_router)
app.include_router(sire_credentials_router)
app.include_router(dashboard_router)
app.include_router(users_router)
app.include_router(export_router)
app.include_router(bot_router)
app.include_router(facturacion_router)
app.include_router(processing_router)
app.include_router(client_auth_router)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Comprobable: curl localhost:8000/health -> {"status": "ok"}
    """
    return {"status": "ok", "service": "contax-brain"}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Contax Brain API",
        "version": "0.2.0",
        "docs": "/docs"
    }


@app.get("/test/supabase")
async def test_supabase():
    """
    Test Supabase connection.
    Comprobable: Returns list of organizations (empty if none created).
    """
    try:
        supabase = get_supabase()
        result = supabase.table("organizations").select("*").execute()
        return {
            "status": "connected",
            "organizations_count": len(result.data),
            "data": result.data
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/test/odoo")
async def test_odoo():
    """
    Test Odoo XML-RPC connection.
    Comprobable: Returns Odoo version and first partner.
    """
    try:
        odoo = get_odoo()
        version = odoo.version()

        try:
            partners = odoo.search_read(
                'res.partner',
                [['is_company', '=', True]],
                ['name', 'vat'],
                limit=1
            )
        except Exception:
            partners = "Auth required - update .env with ODOO_PASSWORD"

        return {
            "status": "connected",
            "odoo_version": version.get("server_version"),
            "first_partner": partners
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
