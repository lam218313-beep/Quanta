"""
Background processing tasks for document analysis.
Integrates OCR extraction and AI classification.
"""
import time
import httpx
from db.supabase_client import get_supabase


def process_document_sync(doc_id: str):
    """
    Synchronous background task to process a document.
    Called by FastAPI's BackgroundTasks.
    
    Pipeline:
    1. Update status to 'analyzing'
    2. Download file from Supabase Storage
    3. Extract text (OCR for images/PDFs, decode for XML)
    4. Classify document type
    5. Extract fields based on type
    6. Update staging_documents with results
    """
    print(f"[RE-START] Starting background processing for document: {doc_id}")
    
    try:
        supabase = get_supabase()
        
        # Step 1: Update status to 'analyzing'
        print(f"   -> Updating status to 'analyzing'")
        supabase.table("staging_documents").update({
            "status": "analyzing"
        }).eq("id", doc_id).execute()
        
        # Get document record
        doc_result = supabase.table("staging_documents")\
            .select("file_url, original_filename")\
            .eq("id", doc_id)\
            .execute()
        
        if not doc_result.data:
            raise Exception("Document not found")
        
        doc = doc_result.data[0]
        file_url = doc['file_url']
        filename = doc.get('original_filename', 'unknown')
        
        # Step 2: Download file
        print(f"   -> Downloading file: {filename}")
        response = httpx.get(file_url, timeout=30)
        file_bytes = response.content
        
        # Determine content type from filename
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        content_type_map = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'xml': 'text/xml',
        }
        content_type = content_type_map.get(ext, 'application/octet-stream')
        
        # Step 3: Extract text
        print(f"   -> Extracting text (type: {content_type})")
        from ai.ocr_engine import get_ocr
        ocr = get_ocr()
        extracted_text = ocr.extract(file_bytes, content_type)
        
        if extracted_text.startswith('[') and 'error' in extracted_text.lower():
            # OCR failed, mark for review
            print(f"   -> OCR failed: {extracted_text}")
            supabase.table("staging_documents").update({
                "status": "review_required",
                "validation_issues": [{"type": "ocr_failed", "message": extracted_text}]
            }).eq("id", doc_id).execute()
            return
        
        # Step 4: Classify and extract fields
        print(f"   -> Classifying document...")
        from ai.classifier import get_classifier
        classifier = get_classifier()
        result = classifier.process(extracted_text)
        
        classification = result['classification']
        extracted_data = result['extracted_data']
        
        print(f"   -> Classification: {classification['type']} ({classification['confidence']*100:.0f}%)")
        
        # Step 5: Run validations
        print(f"   -> Running validations for type: {classification['type']}")
        validation_issues = []
        
        from validation.validators import get_ruc_validator, get_bancarization_validator
        
        # Validate RUC if present
        ruc_value = extracted_data.get('ruc', {}).get('value')
        if ruc_value:
            ruc_validator = get_ruc_validator()
            ruc_result = ruc_validator.validate(ruc_value)
            if not ruc_result.passed:
                validation_issues.append(ruc_result.to_dict())
            print(f"      [DEBUG] RUC check: {ruc_value} -> {ruc_result.passed}")
        
        # Check bancarization if invoice with total
        total_value = extracted_data.get('total', {}).get('value')
        print(f"      [DEBUG] Bancarization check: type={classification['type']}, total={total_value}")
        if classification['type'] == 'invoice' and total_value:
            banc_validator = get_bancarization_validator()
            has_voucher = False  # Will be updated by linking step
            banc_result = banc_validator.validate(total_value, has_voucher)
            if not banc_result.passed:
                validation_issues.append(banc_result.to_dict())
            print(f"      [DEBUG] Bancarization result: {banc_result.passed}")
        
        # Determine final status
        has_errors = any(v.get('severity') == 'error' for v in validation_issues)
        has_warnings = any(v.get('severity') == 'warning' for v in validation_issues)
        
        if has_errors:
            final_status = "review_required"
        elif classification['confidence'] >= 0.6 and extracted_data:
            final_status = "extracted"
        else:
            final_status = "review_required"
        
        # Add low confidence warning if needed
        if classification['confidence'] < 0.6:
            validation_issues.append({
                "rule": "classification_confidence",
                "passed": False,
                "message": f"Classification confidence below threshold: {classification['confidence']*100:.0f}%",
                "severity": "warning"
            })
        
        # Step 6: Update database with results
        print(f"   -> Updating status to '{final_status}'")
        
        update_data = {
            "status": final_status,
            "doc_type": classification['type'],
            "classification_confidence": classification['confidence'],
            "extracted_data": {
                **extracted_data,
                "raw_text_preview": result.get('raw_text_preview', '')[:500]
            },
            "validation_issues": validation_issues if validation_issues else []
        }
        
        supabase.table("staging_documents").update(update_data).eq("id", doc_id).execute()
        
        # Step 7: Attempt auto-linking (Step 5.3)
        if final_status == "extracted" or final_status == "review_required":
            from tasks.processing import attempt_auto_link
            attempt_auto_link(doc_id)
            
        print(f"[DONE] Document {doc_id} processed ({final_status}, {len(validation_issues)} issues)")
        
    except Exception as e:
        print(f"[ERROR] Document {doc_id} processing failed: {e}")
        # On error, mark as 'error' status
        try:
            supabase = get_supabase()
            supabase.table("staging_documents").update({
                "status": "error",
                "validation_issues": [{"type": "processing_error", "message": str(e)}]
            }).eq("id", doc_id).execute()
        except:
            pass


def attempt_auto_link(doc_id: str):
    """
    Tries to find a match for the newly processed document.
    """
    print(f"   -> Attempting auto-link for {doc_id}...")
    try:
        supabase = get_supabase()
        
        # Get the document we just processed
        doc_res = supabase.table("staging_documents").select("*").eq("id", doc_id).execute()
        if not doc_res.data:
            return
        
        target_doc = doc_res.data[0]
        doc_type = target_doc.get("doc_type")
        org_id = target_doc.get("org_id")
        
        if doc_type not in ["invoice", "voucher"]:
            return

        # Search for potential partners (unlinked documents of the other type)
        other_type = "voucher" if doc_type == "invoice" else "invoice"
        
        query = supabase.table("staging_documents")\
            .select("*")\
            .eq("org_id", org_id)\
            .eq("doc_type", other_type)\
            .is_("linked_voucher_id", "null")
            
        partners_res = query.execute()
        if not partners_res.data:
            return
            
        # Use linking validator
        from validation.validators import get_linking_validator
        linker = get_linking_validator()
        
        # We pass all relevant documents to the linker
        all_docs = [target_doc] + partners_res.data
        matches = linker.find_matches(all_docs)
        
        # If we have a high confidence match involving our doc_id, link it
        top_match = None
        for m in matches:
            if m['invoice_id'] == doc_id or m['voucher_id'] == doc_id:
                if m['confidence'] >= 0.8: # Threshold for auto-linking
                    top_match = m
                    break
        
        if top_match:
            inv_id = top_match['invoice_id']
            vouch_id = top_match['voucher_id']
            print(f"      [Auto-link Found] Inv:{inv_id} <-> Vouch:{vouch_id} (conf: {top_match['confidence']})")
            
            # Update invoice with link
            supabase.table("staging_documents").update({
                "linked_voucher_id": vouch_id
            }).eq("id", inv_id).execute()
            
            # Clear bancarization warning from the invoice
            inv_res = supabase.table("staging_documents").select("validation_issues").eq("id", inv_id).execute()
            if inv_res.data:
                issues = inv_res.data[0].get("validation_issues", [])
                if isinstance(issues, list):
                    updated_issues = [
                        issue for issue in issues 
                        if issue.get('rule') != 'bancarization'
                    ]
                    supabase.table("staging_documents").update({
                        "validation_issues": updated_issues,
                        "status": "extracted" if not any(i.get('severity') == 'error' for i in updated_issues) else "review_required"
                    }).eq("id", inv_id).execute()
            
            print(f"      [Auto-link] Warning cleared for invoice {inv_id}")
        
    except Exception as e:
        print(f"      [Auto-link error: {e}]")
