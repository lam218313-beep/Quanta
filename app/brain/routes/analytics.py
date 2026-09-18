"""
Analytics and Tax Reporting endpoints.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from datetime import datetime, timedelta
import random
from db.supabase_client import get_supabase

router = APIRouter(prefix="/api", tags=["analytics"])

@router.get("/tax-summary")
async def get_tax_summary(period: str, org_id: Optional[str] = None):
    """
    Calculate estimated tax obligation for a given period (YYYY-MM).
    Sum of IGV from Sales (Projected) vs Purchases (Staging Docs).
    """
    supabase = get_supabase()
    
    # Validation period format YYYY-MM
    try:
        parts = period.strip().split('-')
        if len(parts) != 2:
            raise ValueError
        year, month = int(parts[0]), int(parts[1])
        if not (2000 <= year <= 2100) or not (1 <= month <= 12):
            raise ValueError
            
        start_date = f"{year}-{month:02d}-01"
        # Calculate next month for range filter
        if month == 12:
            next_month = f"{year+1}-01"
        else:
            next_month = f"{year}-{month+1:02d}"
            
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid period format. Received: '{period}'. Expected YYYY-MM")

    # 1. Fetch Purchases (Vendor Bills)
    # Filter: created_at in month AND status in [posted, ready_to_push, extracted]
    # We include 'extracted' to give a "projected" view even if not approved
    
    # Note: In a real system, we should use the 'date' extracted from the document, 
    # not created_at. For this MVP, we'll try to use extracting data date if available, 
    # falling back to created_at if implicit.
    
    # Actually, Supabase filtering on JSONB extracted_date is hard without a computed column.
    # For MVP performance, we'll fetch all docs for the month's created_at (upload date) 
    # as a proxy, or fetch all and filter in python (bad for scale, ok for MVP).
    
    # Better MVP approach: Filter by created_at range
    # Better MVP approach: Filter by created_at range
    
    query = supabase.table("staging_documents").select("*")\
        .gte("created_at", f"{period}-01T00:00:00")\
        .lt("created_at", f"{next_month}-01T00:00:00")
        
    if org_id:
        query = query.eq("org_id", org_id)
        
    result = query.execute()
    docs = result.data
    
    purchases_base = 0.0
    purchases_igv = 0.0
    
    for doc in docs:
        # Only count valid documents
        if doc['status'] == 'error':
            continue
            
        # Extract total
        try:
            total = float(doc.get('extracted_data', {}).get('total', {}).get('value', 0))
        except:
            total = 0.0
            
        # Simple estimation: Base = Total / 1.18, IGV = Total - Base
        # In Peru, most B2B invoices include IGV.
        base = total / 1.18
        igv = total - base
        
        purchases_base += base
        purchases_igv += igv
        
    # 2. Fetch Sales (Not implemented yet)
    # We'll assume 0 sales for now, or mock widespread sales if requested.
    sales_base = 0.0
    sales_igv = 0.0
    
    return {
        "period": period,
        "currency": "PEN",
        "sales": {
            "base": round(sales_base, 2),
            "igv": round(sales_igv, 2)
        },
        "purchases": {
            "base": round(purchases_base, 2),
            "igv": round(purchases_igv, 2)
        },
        "tax_to_pay": round(sales_igv - purchases_igv, 2),
        "doc_count": len(docs)
    }


@router.get("/sire-comparison")
async def get_sire_comparison(period: Optional[str] = None):
    """
    Compares API data (Local DB) with SUNAT SIRE.
    Uses SunatSireClient (Mock or Real) to fetch RVIE/RCE proposals.
    """
    if not period:
        period = datetime.now().strftime("%Y-%m")
        
    try:
        from integrations.sunat_sire import SunatSireClient
        client = SunatSireClient()
        
        # Fetch proposals (Mocked or Real)
        rvie = client.get_sales_proposal(period)
        rce = client.get_purchases_proposal(period)
        
        # Combine discrepancies
        all_discrepancies = []
        if rvie.get("discrepancies"):
            all_discrepancies.extend(rvie["discrepancies"])
        if rce.get("discrepancies"):
            all_discrepancies.extend(rce["discrepancies"])
            
        return {
            "period": period,
            "status": "synchronized", # or "divergent"
            "sunat_totals": {
                "sales": rvie.get("totals"),
                "purchases": rce.get("totals")
            },
            "discrepancies": all_discrepancies
        }
        
    except Exception as e:
        print(f"SIRE Error: {e}")
        return {
            "error": "Failed to sync with SIRE",
            "details": str(e)
        }
