"""
Client Attachments Routes — Quanta

Lets admin/accountant staff attach extra PDFs (NPS forms, tax filing
receipts, etc.) to a specific client + periodo. These get merged onto the
end of the financial report PDF (see app/brain/routes/pdf.py) whenever
anyone downloads it for that client + periodo.
"""
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from app.brain.db.supabase_client import get_supabase
from app.brain.middleware.auth import require_role, AuthenticatedUser

router = APIRouter(prefix="/api/attachments", tags=["attachments"])

STORAGE_BUCKET = "client-attachments"
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15MB


@router.post("/upload")
async def upload_attachment(
    file: UploadFile = File(...),
    cliente_id: str = Form(...),
    periodo: str = Form(...),
    user: AuthenticatedUser = Depends(require_role("admin", "accountant")),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext != ".pdf":
        raise HTTPException(400, "El archivo debe ser un PDF")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(400, "El archivo supera el límite de 15MB")

    supabase = get_supabase()
    storage_path = f"{cliente_id}/{periodo}/{uuid.uuid4().hex}-{file.filename}"

    try:
        supabase.storage.from_(STORAGE_BUCKET).upload(
            path=storage_path,
            file=content,
            file_options={"content-type": "application/pdf"},
        )
    except Exception as e:
        raise HTTPException(500, f"No se pudo subir el archivo: {e}")

    res = supabase.table("client_attachments").insert({
        "cliente_id": cliente_id,
        "periodo": periodo,
        "nombre_archivo": file.filename,
        "storage_path": storage_path,
        "tamano_bytes": len(content),
        "subido_por": user.user_id,
    }).execute()

    return res.data[0]


@router.get("/{cliente_id}/{periodo}")
async def list_attachments(
    cliente_id: str,
    periodo: str,
    user: AuthenticatedUser = Depends(require_role("admin", "accountant")),
):
    supabase = get_supabase()
    res = (
        supabase.table("client_attachments")
        .select("id, nombre_archivo, tamano_bytes, created_at")
        .eq("cliente_id", cliente_id)
        .eq("periodo", periodo)
        .order("created_at")
        .execute()
    )
    return {"attachments": res.data or []}


@router.delete("/{attachment_id}")
async def delete_attachment(
    attachment_id: str,
    user: AuthenticatedUser = Depends(require_role("admin", "accountant")),
):
    supabase = get_supabase()
    res = supabase.table("client_attachments").select("storage_path").eq("id", attachment_id).execute()
    if not res.data:
        raise HTTPException(404, "Adjunto no encontrado")

    storage_path = res.data[0]["storage_path"]
    try:
        supabase.storage.from_(STORAGE_BUCKET).remove([storage_path])
    except Exception:
        pass  # ya no está en Storage; igual borramos el registro para no dejarlo huérfano

    supabase.table("client_attachments").delete().eq("id", attachment_id).execute()
    return {"status": "ok"}
