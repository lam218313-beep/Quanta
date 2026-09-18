"""
Document linking routes for voucher-invoice matching.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from db.supabase_client import get_supabase
from validation.validators import get_linking_validator


router = APIRouter(prefix="/api", tags=["linking"])


@router.get("/documents/suggest-links")
async def suggest_links(org_id: Optional[str] = None):
    """
    Suggest voucher-invoice links based on amount and date matching.
    
    Returns potential matches with confidence scores.
    """
    supabase = get_supabase()
    
    # Get documents that could be linked
    query = supabase.table("staging_documents")\
        .select("id, doc_type, extracted_data, status")\
        .in_("doc_type", ["invoice", "voucher"])\
        .is_("linked_voucher_id", "null")  # Only unlinked documents
    
    if org_id:
        query = query.eq("org_id", org_id)
    
    result = query.execute()
    documents = result.data or []
    
    # Find matches
    validator = get_linking_validator()
    matches = validator.find_matches(documents)
    
    return {
        "suggestions": matches,
        "invoices_without_voucher": len([d for d in documents if d.get('doc_type') == 'invoice']),
        "vouchers_unlinked": len([d for d in documents if d.get('doc_type') == 'voucher'])
    }


@router.post("/documents/{invoice_id}/link/{voucher_id}")
async def link_documents(invoice_id: str, voucher_id: str):
    """
    Link a voucher to an invoice (for bancarization compliance).
    
    Updates both documents to reference each other.
    """
    supabase = get_supabase()
    
    # Verify both documents exist
    invoice = supabase.table("staging_documents")\
        .select("id, doc_type, extracted_data")\
        .eq("id", invoice_id)\
        .execute()
    
    voucher = supabase.table("staging_documents")\
        .select("id, doc_type, extracted_data")\
        .eq("id", voucher_id)\
        .execute()
    
    if not invoice.data:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if not voucher.data:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    if invoice.data[0].get('doc_type') != 'invoice':
        raise HTTPException(status_code=400, detail="First document must be an invoice")
    if voucher.data[0].get('doc_type') != 'voucher':
        raise HTTPException(status_code=400, detail="Second document must be a voucher")
    
    # Update invoice with linked voucher
    supabase.table("staging_documents").update({
        "linked_voucher_id": voucher_id
    }).eq("id", invoice_id).execute()
    
    # Clear bancarization warning from validation_issues
    inv_data = invoice.data[0]
    current_issues = inv_data.get('validation_issues', [])
    if isinstance(current_issues, list):
        updated_issues = [
            issue for issue in current_issues 
            if issue.get('rule') != 'bancarization'
        ]
        supabase.table("staging_documents").update({
            "validation_issues": updated_issues
        }).eq("id", invoice_id).execute()
    
    return {
        "status": "linked",
        "invoice_id": invoice_id,
        "voucher_id": voucher_id,
        "message": "Voucher linked to invoice. Bancarization requirement satisfied."
    }


@router.delete("/documents/{invoice_id}/unlink")
async def unlink_documents(invoice_id: str):
    """
    Remove voucher link from an invoice.
    """
    supabase = get_supabase()
    
    supabase.table("staging_documents").update({
        "linked_voucher_id": None
    }).eq("id", invoice_id).execute()
    
    return {
        "status": "unlinked",
        "invoice_id": invoice_id,
        "message": "Voucher link removed."
    }
