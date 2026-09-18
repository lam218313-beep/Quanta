"""
SIRE API Routes
Endpoints for downloading and comparing SUNAT SIRE data per client
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Literal
from pydantic import BaseModel
import logging

from integrations.sunat_sire import SunatSireClient
from db.supabase_client import get_supabase
from utils.encryption import decrypt_credential

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/clients", tags=["SIRE"])


class SireDownloadRequest(BaseModel):
    period: str  # YYYYMM format (e.g., "202401")
    book_type: Literal["sales", "purchases"]


class SireDownloadResponse(BaseModel):
    success: bool
    period: str
    book_type: str
    voucher_count: int
    message: str


@router.post("/{client_id}/sire/download", response_model=SireDownloadResponse)
async def download_sire_vouchers(
    client_id: str,
    request: SireDownloadRequest
):
    """
    Download SIRE vouchers (sales or purchases) for a specific client
    
    This endpoint:
    1. Retrieves encrypted SOL credentials from database
    2. Decrypts credentials
    3. Initializes SIRE client
    4. Downloads vouchers from SUNAT
    5. Saves vouchers to database
    
    Args:
        client_id: Client UUID
        request: Download request with period and book_type
    
    Returns:
        Download status and voucher count
    """
    try:
        supabase = get_supabase()
        
        # Step 1: Get client credentials from database
        logger.info(f"Fetching credentials for client {client_id}")
        
        result = supabase.table("clients").select(
            "sol_client_id, sol_client_secret, sol_username, sol_password, ruc, business_name"
        ).eq("id", client_id).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Client not found")
        
        client_data = result.data
        
        # Step 2: Decrypt credentials
        try:
            client_id_decrypted = decrypt_credential(client_data["sol_client_id"])
            client_secret_decrypted = decrypt_credential(client_data["sol_client_secret"])
            username_decrypted = decrypt_credential(client_data["sol_username"])
            password_decrypted = decrypt_credential(client_data["sol_password"])
        except Exception as e:
            logger.error(f"Failed to decrypt credentials: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to decrypt SOL credentials. Please re-enter credentials."
            )
        
        # Step 3: Initialize SIRE client
        sire_client = SunatSireClient(
            client_id=client_id_decrypted,
            client_secret=client_secret_decrypted,
            ruc=client_data["ruc"],
            username=username_decrypted,
            password=password_decrypted
        )
        
        # Step 4: Download vouchers
        logger.info(f"Downloading {request.book_type} for period {request.period}")
        
        vouchers = sire_client.download_vouchers(
            period=request.period,
            book_type=request.book_type
        )
        
        # Step 5: Save vouchers to database
        logger.info(f"Saving {len(vouchers)} vouchers to database")
        
        for voucher in vouchers:
            # Prepare document record
            doc_data = {
                "client_id": client_id,
                "type": "invoice" if voucher["type"] in ["01", "03"] else "credit_note",
                "series": voucher["series"],
                "number": voucher["number"],
                "date": voucher["date"],
                "ruc_issuer": voucher["ruc_issuer"],
                "total": voucher["total"],
                "igv": voucher["igv"],
                "source": "sire",
                "book_type": request.book_type,
                "raw_data": voucher
            }
            
            # Upsert (insert or update if exists)
            supabase.table("documents").upsert(
                doc_data,
                on_conflict="client_id,series,number"
            ).execute()
        
        logger.info(f"Successfully saved {len(vouchers)} vouchers")
        
        return SireDownloadResponse(
            success=True,
            period=request.period,
            book_type=request.book_type,
            voucher_count=len(vouchers),
            message=f"Successfully downloaded and saved {len(vouchers)} {request.book_type} vouchers"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading SIRE vouchers: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download SIRE vouchers: {str(e)}"
        )


@router.get("/{client_id}/sire/comparison")
async def get_sire_comparison(
    client_id: str,
    period: str
):
    """
    Compare local documents vs SIRE documents for a period
    
    Returns discrepancies:
    - Missing in SIRE (local only)
    - Missing locally (SIRE only)
    - Amount mismatches
    
    Args:
        client_id: Client UUID
        period: Period in YYYYMM format
    
    Returns:
        Comparison results with discrepancies
    """
    try:
        supabase = get_supabase()
        
        # Get all documents for this client and period
        result = supabase.table("documents").select("*").eq(
            "client_id", client_id
        ).execute()
        
        documents = result.data
        
        # Separate by source
        local_docs = {
            f"{d['series']}-{d['number']}": d
            for d in documents
            if d.get("source") == "local"
        }
        
        sire_docs = {
            f"{d['series']}-{d['number']}": d
            for d in documents
            if d.get("source") == "sire"
        }
        
        # Find discrepancies
        discrepancies = []
        
        # Missing in SIRE
        for ref, doc in local_docs.items():
            if ref not in sire_docs:
                discrepancies.append({
                    "severity": "medium",
                    "type": "missing_sunat",
                    "message": f"Documento {ref} no aparece en SUNAT",
                    "local": {
                        "ref": ref,
                        "total": doc["total"]
                    },
                    "sunat": None
                })
        
        # Missing locally
        for ref, doc in sire_docs.items():
            if ref not in local_docs:
                discrepancies.append({
                    "severity": "high",
                    "type": "missing_local",
                    "message": f"Documento {ref} aparece en SUNAT pero no localmente",
                    "local": None,
                    "sunat": {
                        "ref": ref,
                        "total": doc["total"]
                    }
                })
        
        # Amount mismatches
        for ref in set(local_docs.keys()) & set(sire_docs.keys()):
            local_total = local_docs[ref]["total"]
            sire_total = sire_docs[ref]["total"]
            
            if abs(local_total - sire_total) > 0.01:  # Tolerance for float comparison
                discrepancies.append({
                    "severity": "high",
                    "type": "mismatch",
                    "message": f"Monto diferente para {ref}",
                    "local": {
                        "ref": ref,
                        "total": local_total
                    },
                    "sunat": {
                        "ref": ref,
                        "total": sire_total
                    }
                })
        
        # Calculate totals
        sire_sales_total = sum(d["total"] for d in sire_docs.values() if d.get("book_type") == "sales")
        sire_purchases_total = sum(d["total"] for d in sire_docs.values() if d.get("book_type") == "purchases")
        
        return {
            "period": period,
            "status": "synchronized" if len(discrepancies) == 0 else "discrepancies_found",
            "sunat_totals": {
                "sales": {
                    "taxable_base": sire_sales_total / 1.18,  # Approximate
                    "igv": sire_sales_total * 0.18 / 1.18,
                    "total": sire_sales_total
                },
                "purchases": {
                    "taxable_base": sire_purchases_total / 1.18,
                    "igv": sire_purchases_total * 0.18 / 1.18,
                    "total": sire_purchases_total
                }
            },
            "discrepancies": discrepancies
        }
        
    except Exception as e:
        logger.error(f"Error comparing SIRE data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare SIRE data: {str(e)}"
        )
