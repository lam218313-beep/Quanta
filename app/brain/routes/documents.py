"""
File upload and document ingestion routes.
"""
import hashlib
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from db.supabase_client import get_supabase


router = APIRouter(prefix="/api", tags=["documents"])


class UploadResponse(BaseModel):
    file_id: str
    file_url: str
    status: str
    original_filename: str
    message: str


@router.post("/upload", status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    org_id: Optional[str] = None  # Will be extracted from JWT in production
):
    """
    Upload a document (PDF, XML, JPG, PNG) for processing.
    
    Returns 202 Accepted immediately, processing happens in background.
    
    Steps:
    1. Calculate file hash (SHA-256) for duplicate detection
    2. Upload to Supabase Storage bucket 'uploads'
    3. Create record in staging_documents with status 'queued'
    4. Queue background task for AI processing
    5. Return file_id for tracking (client can poll for status)
    """
    # Validate file type
    allowed_types = ['application/pdf', 'text/xml', 'application/xml', 
                     'image/jpeg', 'image/png']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type: {file.content_type}. Allowed: PDF, XML, JPG, PNG"
        )
    
    try:
        supabase = get_supabase()
        
        # Read file content
        content = await file.read()
        
        # Calculate hash for duplicate detection
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Generate unique filename
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
        storage_path = f"{org_id or 'default'}/{uuid.uuid4()}.{file_ext}"
        
        # Upload to Supabase Storage
        storage_result = supabase.storage.from_("uploads").upload(
            path=storage_path,
            file=content,
            file_options={"content-type": file.content_type}
        )
        
        # Get public URL
        file_url = supabase.storage.from_("uploads").get_public_url(storage_path)
        
        # Create staging record
        doc_record = {
            "org_id": org_id or "00000000-0000-0000-0000-000000000000",  # Default for testing
            "file_url": file_url,
            "original_filename": file.filename,
            "file_hash": file_hash,
            "status": "queued"
        }
        
        insert_result = supabase.table("staging_documents").insert(doc_record).execute()
        
        if not insert_result.data:
            raise HTTPException(status_code=500, detail="Failed to create document record")
        
        created_doc = insert_result.data[0]
        doc_id = created_doc["id"]
        
        # Queue background processing task
        # Note: BackgroundTasks runs sync functions, we'll call the async one properly
        from tasks.processing import process_document_sync
        background_tasks.add_task(process_document_sync, doc_id)
        
        # Return 202 Accepted immediately
        return JSONResponse(
            status_code=202,
            content={
                "file_id": doc_id,
                "file_url": file_url,
                "status": "queued",
                "original_filename": file.filename,
                "message": "Document queued for processing. Poll GET /api/documents/{id} for status."
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/documents")
async def list_documents(
    org_id: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    List documents with advanced filtering and pagination.
    """
    supabase = get_supabase()
    
    # Base query
    query = supabase.table("staging_documents").select("*", count="exact")
    
    # Organization filter
    if org_id:
        query = query.eq("org_id", org_id)
        
    # Status filter
    if status:
        query = query.eq("status", status)
        
    # Date filtering (on created_at for now, could be on extracted date later)
    if date_from:
        query = query.gte("created_at", f"{date_from}T00:00:00")
    if date_to:
        query = query.lte("created_at", f"{date_to}T23:59:59")
        
    # Search filter (Supabase ILIKE)
    if search:
        # Search in filename only for now as JSONB search is complex via ORM
        # Ideally we'd search in extracted_data too
        query = query.ilike("original_filename", f"%{search}%")
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size - 1
    
    result = query.order("created_at", desc=True).range(start, end).execute()
    
    total_count = result.count if result.count is not None else 0
    total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
    
    return {
        "status": "success",
        "data": result.data,
        "meta": {
            "current_page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages
        }
    }


@router.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """
    Get a single document with all details.
    """
    supabase = get_supabase()
    
    result = supabase.table("staging_documents").select("*").eq("id", doc_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return result.data[0]


@router.get("/documents/{doc_id}/preview")
async def get_document_preview(doc_id: str):
    """
    Generate a temporary signed URL for viewing the document.
    """
    supabase = get_supabase()
    
    # 1. Get document to find original file path (or reconstruct it)
    doc_res = supabase.table("staging_documents").select("file_url, org_id").eq("id", doc_id).execute()
    if not doc_res.data:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = doc_res.data[0]
    file_url = doc.get("file_url", "")
    
    # Extract path from public URL if possible, or query it
    # Format: .../storage/v1/object/public/uploads/{org_id}/{uuid}.{ext}
    # We need: {org_id}/{uuid}.{ext}
    if "/uploads/" in file_url:
        storage_path = file_url.split("/uploads/")[-1]
    else:
        # Fallback if URL format changed
        raise HTTPException(status_code=500, detail="Could not determine storage path")
    
    try:
        # 2. Generate signed URL (valid for 1 hour)
        signed_url = supabase.storage.from_("uploads").create_signed_url(
            path=storage_path, 
            expires_in=3600
        )
        
        # Depending on Supabase SDK version, signed_url might be a dict or string
        # Modern client: {'signedURL': '...'} or string
        url = signed_url.get("signedURL") if isinstance(signed_url, dict) else signed_url
        
        return {
            "doc_id": doc_id,
            "preview_url": url,
            "expires_in_seconds": 3600
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(e)}")


@router.patch("/documents/{doc_id}")
async def update_document(doc_id: str, updates: dict):
    """
    Update document extracted data (Human Correction).
    Triggers re-validation.
    """
    supabase = get_supabase()
    
    # 1. Fetch current doc
    current = supabase.table("staging_documents").select("*").eq("id", doc_id).execute()
    if not current.data:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = current.data[0]
    new_data = doc.get("extracted_data", {})
    
    # 2. Merge updates into extracted_data
    if "extracted_data" in updates:
        # Deep merge could be better, but simple merge for now
        for key, val in updates["extracted_data"].items():
            new_data[key] = val
            
    # 3. Re-run validations (Bancarization check needs up-to-date total)
    validation_issues = doc.get("validation_issues", [])
    
    # Remove old bancarization issues to re-evaluate
    validation_issues = [i for i in validation_issues if i.get("rule") != "bancarization"]
    
    if doc.get("doc_type") == "invoice":
        total_value = float(new_data.get("total", {}).get("value", 0))
        has_voucher = doc.get("linked_voucher_id") is not None
        
        from validation.validators import get_bancarization_validator
        banc_validator = get_bancarization_validator()
        res = banc_validator.validate(total_value, has_voucher)
        
        if not res.passed:
            validation_issues.append(res.to_dict())
            
    # 4. Save updates
    update_payload = {
        "extracted_data": new_data,
        "validation_issues": validation_issues,
        "status": "ready_to_push" if not any(i['severity'] == 'error' for i in validation_issues) else "review_required"
    }
    
    supabase.table("staging_documents").update(update_payload).eq("id", doc_id).execute()
    
    return {"status": "updated", "doc_id": doc_id, "new_status": update_payload["status"]}


@router.post("/documents/{doc_id}/approve")
async def approve_document(doc_id: str):
    """
    Approve document and push to Odoo.
    """
    supabase = get_supabase()
    
    # 1. Fetch doc
    doc_res = supabase.table("staging_documents").select("*").eq("id", doc_id).execute()
    if not doc_res.data:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = doc_res.data[0]
    
    # 2. Check status
    # We allow pushing even if review_required if user forces it (approve action implies force)
    # But ideally, errors should be resolved.
    
    from db.odoo_client import get_odoo
    odoo = get_odoo()
    
    try:
        # 3. Create Vendor Bill in Odoo
        move_id = odoo.create_vendor_bill(doc.get("extracted_data", {}))
        
        # 4. Update status in Supabase
        supabase.table("staging_documents").update({
            "status": "posted",
            "odoo_move_id": str(move_id)
        }).eq("id", doc_id).execute()
        
        return {
            "status": "posted",
            "odoo_move_id": move_id,
            "message": "Document successfully created in Odoo"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Odoo Push Failed: {str(e)}")
