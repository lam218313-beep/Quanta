"""
Contax Brain API - Main Entry Point
The AI Orchestration Layer for Peruvian Accounting Automation
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from db.supabase_client import get_supabase
from db.odoo_client import get_odoo
from routes.documents import router as documents_router
from routes.linking import router as linking_router
from routes.analytics import router as analytics_router
from routes.pdf import router as pdf_router

# Initialize FastAPI app
app = FastAPI(
    title="Contax Brain API",
    description="AI-powered accounting automation for Peru",
    version="0.1.0"
)

# CORS Configuration (for Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents_router)
app.include_router(linking_router)
app.include_router(analytics_router)
app.include_router(pdf_router)


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
        "version": "0.1.0",
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
        
        # Try to get first partner (may fail if no auth configured)
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
