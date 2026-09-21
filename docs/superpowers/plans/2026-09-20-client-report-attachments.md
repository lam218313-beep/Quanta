# Client Report Attachments Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let admin/accountant staff upload PDFs (NPS forms, tax filing proof, etc.) per client+period, merged onto the end of the same financial report PDF the client already downloads from the Dashboard.

**Architecture:** A new `client_attachments` table + private Storage bucket hold the uploaded files. A new FastAPI router exposes upload/list/delete, gated by the existing `require_role` auth dependency. `/api/pdf/report` merges any matching attachments onto the generated report with PyMuPDF right before serving it. The frontend gets a new drop-zone component, mounted at the bottom of `DashboardView.jsx`, visible only for admin/accountant.

**Tech Stack:** FastAPI + Supabase (Postgres + Storage) on the backend, React + Vite on the frontend, PyMuPDF (`fitz`, already in `requirements.txt`) for PDF merging.

**Spec:** `docs/superpowers/specs/2026-09-20-client-report-attachments-design.md`

## Global Constraints

- Only `.pdf` files are accepted, validated on both frontend and backend.
- Max file size: 15MB per attachment.
- Attachments are scoped to `(cliente_id, periodo)` — never global to a client.
- Only `admin` and `accountant` roles can upload/list/delete attachments; `client` never sees this UI.
- Merging must never break the base report download — a bad attachment is skipped and logged, not fatal.
- No new Python or npm dependencies (PyMuPDF is already installed).

---

### Task 1: Database migration — table, RLS, and storage bucket

**Files:**
- Create: `supabase/migrations/20260920_client_attachments.sql`

**Interfaces:**
- Produces: table `public.client_attachments` with columns `id uuid`, `cliente_id uuid`, `periodo varchar(6)`, `nombre_archivo text`, `storage_path text`, `tamano_bytes integer`, `subido_por uuid`, `created_at timestamptz`. Storage bucket id `client-attachments` (private). Both are consumed by Task 2 and Task 3.

- [ ] **Step 1: Write the migration file**

```sql
-- supabase/migrations/20260920_client_attachments.sql
-- Lets admin/accountant staff attach extra PDFs (NPS, constancias de
-- declaración, etc.) to a specific client + periodo. Merged onto the
-- financial report PDF at download time (see app/brain/routes/pdf.py).
CREATE TABLE public.client_attachments (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id uuid NOT NULL REFERENCES public.clientes(id) ON DELETE CASCADE,
    periodo varchar(6) NOT NULL,
    nombre_archivo text NOT NULL,
    storage_path text NOT NULL,
    tamano_bytes integer,
    subido_por uuid REFERENCES public.user_profiles(id),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_client_attachments_cliente_periodo
    ON public.client_attachments (cliente_id, periodo);

ALTER TABLE public.client_attachments ENABLE ROW LEVEL SECURITY;

-- Same three-policy pattern already used on public.clientes.
CREATE POLICY admin_all_attachments ON public.client_attachments
    FOR ALL USING (get_user_role() = 'admin');

CREATE POLICY accountant_assigned_attachments ON public.client_attachments
    FOR ALL USING (
        get_user_role() = 'accountant'
        AND cliente_id IN (SELECT get_user_cliente_ids())
    );

CREATE POLICY client_own_attachments ON public.client_attachments
    FOR SELECT USING (cliente_id IN (SELECT get_user_cliente_ids()));

-- Private bucket. Backend uses the service_role key (bypasses RLS); no
-- storage.objects policy is needed since there is no public/direct URL,
-- same as the comprobantes-fisicos bucket.
INSERT INTO storage.buckets (id, name, public)
VALUES ('client-attachments', 'client-attachments', false)
ON CONFLICT (id) DO NOTHING;
```

- [ ] **Step 2: Apply the migration**

Use the Supabase MCP `apply_migration` tool against project `nuuqkwdopdsgokiziyum`, with `name` = `client_attachments` and the SQL content from Step 1 as `query`.

- [ ] **Step 3: Verify the table, policies, and bucket exist**

Run this query via the Supabase MCP `execute_sql` tool (same project):

```sql
SELECT
  (SELECT count(*) FROM information_schema.tables
     WHERE table_schema='public' AND table_name='client_attachments') AS tabla,
  (SELECT count(*) FROM pg_policy WHERE polrelid = 'public.client_attachments'::regclass) AS politicas,
  (SELECT count(*) FROM storage.buckets WHERE id='client-attachments') AS bucket;
```

Expected: `tabla=1`, `politicas=3`, `bucket=1`.

- [ ] **Step 4: Commit**

```bash
git add supabase/migrations/20260920_client_attachments.sql
git commit -m "Add client_attachments table, RLS policies, and storage bucket"
```

---

### Task 2: Backend attachments router (upload, list, delete)

**Files:**
- Create: `app/brain/routes/attachments.py`
- Modify: `app/api.py:46` (add import), `app/api.py:136` (mount router)

**Interfaces:**
- Consumes: `get_supabase()` from `app.brain.db.supabase_client` (returns a `supabase.Client`, service-role, bypasses RLS). `require_role(*roles)` and `AuthenticatedUser` from `app.brain.middleware.auth` (`AuthenticatedUser.user_id: str`, `.role: str`, `.cliente_id: Optional[str]`, `.email: str`).
- Produces: `router` (FastAPI `APIRouter`, prefix `/api/attachments`) with:
  - `POST /api/attachments/upload` — multipart form (`file`, `cliente_id`, `periodo`) → `{"id", "cliente_id", "periodo", "nombre_archivo", "storage_path", "tamano_bytes", "subido_por", "created_at"}`
  - `GET /api/attachments/{cliente_id}/{periodo}` → `{"attachments": [{"id", "nombre_archivo", "tamano_bytes", "created_at"}, ...]}`
  - `DELETE /api/attachments/{attachment_id}` → `{"status": "ok"}`

  These are consumed by Task 5 (frontend `AttachmentsDropzone.jsx`) and Task 3 (PDF merge reads the same table directly, not through this router).

- [ ] **Step 1: Write the router**

```python
# app/brain/routes/attachments.py
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
```

- [ ] **Step 2: Mount the router in `app/api.py`**

Add the import next to the other route imports (after line 45, `from app.brain.routes.client_auth import router as client_auth_router`):

```python
from app.brain.routes.attachments import router as attachments_router
```

Add the mount call next to the other `include_router` calls (after line 136, `app.include_router(client_auth_router)`):

```python
app.include_router(attachments_router)
```

- [ ] **Step 3: Verify dependencies are importable**

```bash
cd "D:/2.-Quanta/1.- Quanta_sistema"
python -m py_compile app/brain/routes/attachments.py app/api.py
```

Expected: no output (success).

- [ ] **Step 4: Start the backend locally**

```bash
cd "D:/2.-Quanta/1.- Quanta_sistema"
uvicorn app.api:app --reload --port 8000
```

Expected: `Application startup complete.` with no import errors. Leave this running for the next steps (open a second terminal).

- [ ] **Step 5: Get a real cliente_id and a valid admin JWT for testing**

In a second terminal, query one client's id:

```bash
curl -s "http://localhost:8000/health"
```

Expected: `{"status":"ok", ...}` (confirms the server responds). For the auth token, log into the deployed frontend as `admin@quanta.pe`, open the browser devtools console, and run:

```js
(await window.supabase.auth.getSession()).data.session.access_token
```

Copy that token — it is a real Supabase JWT valid against the same project the local backend's `app/.env` points to. Also grab any client's UUID from the `clientes` table (e.g. via the Supabase dashboard's table editor) — call it `<CLIENTE_ID>`.

- [ ] **Step 6: Test the upload endpoint against a real PDF**

Create a tiny throwaway PDF to upload:

```bash
cd "D:/2.-Quanta/1.- Quanta_sistema"
printf '%%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>' > /tmp/test-attachment.pdf
curl -s -X POST "http://localhost:8000/api/attachments/upload" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@/tmp/test-attachment.pdf" \
  -F "cliente_id=<CLIENTE_ID>" \
  -F "periodo=202608"
```

Expected: a JSON object with `"nombre_archivo":"test-attachment.pdf"` and a generated `"id"`. Copy that `id` — call it `<ATTACHMENT_ID>`.

- [ ] **Step 7: Test the list endpoint**

```bash
curl -s "http://localhost:8000/api/attachments/<CLIENTE_ID>/202608" \
  -H "Authorization: Bearer <TOKEN>"
```

Expected: `{"attachments":[{"id":"<ATTACHMENT_ID>", "nombre_archivo":"test-attachment.pdf", ...}]}`.

- [ ] **Step 8: Test rejection of a non-PDF file**

```bash
echo "not a pdf" > /tmp/test.txt
curl -s -o /dev/null -w "%{http_code}\n" -X POST "http://localhost:8000/api/attachments/upload" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@/tmp/test.txt" \
  -F "cliente_id=<CLIENTE_ID>" \
  -F "periodo=202608"
```

Expected: `400`.

- [ ] **Step 9: Test the delete endpoint**

```bash
curl -s -X DELETE "http://localhost:8000/api/attachments/<ATTACHMENT_ID>" \
  -H "Authorization: Bearer <TOKEN>"
```

Expected: `{"status":"ok"}`. Re-run Step 7's list call and confirm the array is now empty.

- [ ] **Step 10: Test that a client-role token is rejected**

Log into the frontend as a `client`-role test account, grab their token the same way as Step 5, and repeat Step 6 with that token instead.

Expected: HTTP `403` with a body containing `"Rol requerido: admin, accountant"`.

- [ ] **Step 11: Commit**

```bash
git add app/brain/routes/attachments.py app/api.py
git commit -m "Add /api/attachments upload/list/delete endpoints"
```

---

### Task 3: Merge attachments into `/api/pdf/report`

**Files:**
- Modify: `app/brain/routes/pdf.py:1-10` (imports), `app/brain/routes/pdf.py:182-189` (`generate_report_pdf`'s final block)

**Interfaces:**
- Consumes: `get_supabase()` (already imported in this file), the `client_attachments` table from Task 1 (columns `storage_path`, `created_at`), `STORAGE_BUCKET = "client-attachments"` (same bucket name as Task 2 — duplicated here as a local constant rather than a shared import, matching how this codebase already repeats small constants per file).
- Produces: no new interface — `POST /api/pdf/report` keeps its existing request/response shape (`ReportRequest` in → `FileResponse` PDF out); attachments are transparently appended when present.

- [ ] **Step 1: Add the `fitz` import**

In `app/brain/routes/pdf.py`, add this import alongside the existing ones at the top of the file (after `from app.brain.db.supabase_client import get_supabase`):

```python
import fitz  # PyMuPDF
```

- [ ] **Step 2: Read the current end of `generate_report_pdf`**

Confirm the block you're about to replace looks like this (it was written before this plan and should be unchanged):

```python
    output_filename = f"report_{req.cliente_id}_{req.periodo}.pdf"
    output_path = os.path.join(TEMP_DIR, output_filename)

    try:
        await generate_financial_report_pdf(report_data, output_path)
        return FileResponse(path=output_path, filename=f"Informe_{req.periodo}.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(500, f"Error generando el informe: {str(e)}")
```

- [ ] **Step 3: Replace it with the merge-aware version**

```python
    output_filename = f"report_{req.cliente_id}_{req.periodo}.pdf"
    output_path = os.path.join(TEMP_DIR, output_filename)

    try:
        await generate_financial_report_pdf(report_data, output_path)
    except Exception as e:
        raise HTTPException(500, f"Error generando el informe: {str(e)}")

    _merge_attachments(supabase, output_path, req.cliente_id, req.periodo)

    return FileResponse(path=output_path, filename=f"Informe_{req.periodo}.pdf", media_type="application/pdf")


def _merge_attachments(supabase, report_path: str, cliente_id: str, periodo: str) -> None:
    """
    Appends every client_attachments PDF for this cliente+periodo onto the
    end of the report at report_path, in upload order. Never raises — a
    bad attachment is skipped and logged, the base report is always served.
    """
    STORAGE_BUCKET = "client-attachments"

    try:
        res = (
            supabase.table("client_attachments")
            .select("storage_path")
            .eq("cliente_id", cliente_id)
            .eq("periodo", periodo)
            .order("created_at")
            .execute()
        )
        attachments = res.data or []
    except Exception as e:
        print(f"[attachments] No se pudo consultar client_attachments: {e}")
        return

    if not attachments:
        return

    report_doc = fitz.open(report_path)
    merged_any = False

    for att in attachments:
        try:
            content = supabase.storage.from_(STORAGE_BUCKET).download(att["storage_path"])
            attachment_doc = fitz.open(stream=content, filetype="pdf")
            report_doc.insert_pdf(attachment_doc)
            attachment_doc.close()
            merged_any = True
        except Exception as e:
            print(f"[attachments] No se pudo fusionar {att['storage_path']}: {e}")
            continue

    if merged_any:
        report_doc.saveIncr() if report_doc.can_save_incrementally() else report_doc.save(report_path, incremental=False)
    report_doc.close()
```

Note on `saveIncr()` vs `save()`: `fitz.open(report_path)` opens the file from disk by path, so PyMuPDF can save incrementally back onto the same path; if incremental save isn't available for any reason it falls back to a full rewrite of the same path.

- [ ] **Step 4: Verify it compiles**

```bash
cd "D:/2.-Quanta/1.- Quanta_sistema"
python -m py_compile app/brain/routes/pdf.py
```

Expected: no output.

- [ ] **Step 5: Manual end-to-end test — no attachments**

With the backend still running from Task 2 (`uvicorn app.api:app --reload --port 8000`), pick a client+periodo that has NO attachments (any period you haven't uploaded to yet) and request the report:

```bash
curl -s -X POST "http://localhost:8000/api/pdf/report" \
  -H "Content-Type: application/json" \
  -d '{"cliente_id": "<CLIENTE_ID>", "periodo": "202607"}' \
  -o /tmp/informe_sin_adjuntos.pdf
python -c "import fitz; print(fitz.open('/tmp/informe_sin_adjuntos.pdf').page_count)"
```

Expected: prints the report's normal page count (unchanged from before this task — confirms the no-attachments path is a no-op).

- [ ] **Step 6: Manual end-to-end test — with an attachment**

Repeat Task 2 Step 6 (upload `test-attachment.pdf`, a 1-page PDF) for `<CLIENTE_ID>` + periodo `202607`, then re-request the report for the same cliente+periodo:

```bash
curl -s -X POST "http://localhost:8000/api/pdf/report" \
  -H "Content-Type: application/json" \
  -d '{"cliente_id": "<CLIENTE_ID>", "periodo": "202607"}' \
  -o /tmp/informe_con_adjunto.pdf
python -c "import fitz; print(fitz.open('/tmp/informe_con_adjunto.pdf').page_count)"
```

Expected: the page count from Step 5 plus 1 (the merged attachment page). Open both PDFs and visually confirm the last page is the uploaded attachment's content.

- [ ] **Step 7: Clean up the test attachment**

Delete it via `DELETE /api/attachments/<ATTACHMENT_ID>` (Task 2 Step 9) so it doesn't linger in a real client's report.

- [ ] **Step 8: Commit**

```bash
git add app/brain/routes/pdf.py
git commit -m "Merge client_attachments PDFs onto the generated report"
```

---

### Task 4: Thread `userRole` into `DashboardView`

**Files:**
- Modify: `frontend/src/App.jsx` (wherever `<DashboardView` is rendered)
- Modify: `frontend/src/components/DashboardView.jsx:41`

**Interfaces:**
- Consumes: `userRole` state, already set in `App.jsx` (`const [userRole, setUserRole] = useState(null)`, populated by `fetchUserRole`).
- Produces: `DashboardView` now accepts a `userRole` prop (`string | null`, one of `"admin"`, `"accountant"`, `"client"`), consumed by Task 5.

- [ ] **Step 1: Find where `<DashboardView` is rendered in `App.jsx`**

```bash
cd "D:/2.-Quanta/1.- Quanta_sistema/frontend/src"
grep -n "<DashboardView" App.jsx
```

- [ ] **Step 2: Add the `userRole` prop at that call site**

Wherever `grep` found it, the call currently looks like:

```jsx
<DashboardView currentClient={currentClient} selectedPeriodo={selectedPeriodo} />
```

Change it to:

```jsx
<DashboardView currentClient={currentClient} selectedPeriodo={selectedPeriodo} userRole={userRole} />
```

(If `currentClient`/`selectedPeriodo` are computed differently than shown here, keep whatever is already there and only add ` userRole={userRole}`.)

- [ ] **Step 3: Accept the prop in `DashboardView.jsx`**

Change line 41 from:

```jsx
export default function DashboardView({ currentClient, selectedPeriodo }) {
```

to:

```jsx
export default function DashboardView({ currentClient, selectedPeriodo, userRole }) {
```

- [ ] **Step 4: Verify it renders with no console errors**

```bash
cd "D:/2.-Quanta/1.- Quanta_sistema/frontend"
npm run dev
```

Open the printed local URL in a browser, log in, select any client, and open the Dashboard tab. Expected: dashboard renders exactly as before (no visual change yet — this task only threads the prop, Task 5 uses it). Open the browser devtools console and confirm there are no new errors.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/App.jsx frontend/src/components/DashboardView.jsx
git commit -m "Pass userRole down to DashboardView"
```

---

### Task 5: `AttachmentsDropzone` component, wired into `DashboardView`

**Files:**
- Create: `frontend/src/components/AttachmentsDropzone.jsx`
- Modify: `frontend/src/components/DashboardView.jsx:1-13` (imports), `frontend/src/components/DashboardView.jsx:525` (render)

**Interfaces:**
- Consumes: `require_role`-gated endpoints from Task 2 (`POST /api/attachments/upload`, `GET /api/attachments/{cliente_id}/{periodo}`, `DELETE /api/attachments/{attachment_id}`), the `supabase` client from `../supabaseClient` (for `supabase.auth.getSession()`), `userRole` prop from Task 4.
- Produces: `AttachmentsDropzone` component accepting props `{ clienteId: string, periodo: string, apiBaseUrl: string }`. No other file depends on its internals — `DashboardView` only renders it.

- [ ] **Step 1: Write the component**

```jsx
// frontend/src/components/AttachmentsDropzone.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { Upload, Trash2, FileText, Loader2 } from 'lucide-react';
import { supabase } from '../supabaseClient';

export default function AttachmentsDropzone({ clienteId, periodo, apiBaseUrl }) {
  const [attachments, setAttachments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState(null);

  const authHeader = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    return { Authorization: `Bearer ${session?.access_token}` };
  };

  const loadAttachments = useCallback(async () => {
    if (!clienteId || !periodo) return;
    setLoading(true);
    try {
      const headers = await authHeader();
      const res = await fetch(`${apiBaseUrl}/api/attachments/${clienteId}/${periodo}`, { headers });
      if (!res.ok) throw new Error('No se pudo cargar la lista de adjuntos');
      const data = await res.json();
      setAttachments(data.attachments || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [clienteId, periodo, apiBaseUrl]);

  useEffect(() => {
    loadAttachments();
  }, [loadAttachments]);

  const uploadFile = async (file) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Solo se aceptan archivos .pdf');
      return;
    }
    setUploading(true);
    setError(null);
    try {
      const headers = await authHeader();
      const formData = new FormData();
      formData.append('file', file);
      formData.append('cliente_id', clienteId);
      formData.append('periodo', periodo);
      const res = await fetch(`${apiBaseUrl}/api/attachments/upload`, {
        method: 'POST',
        headers,
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'No se pudo subir el archivo');
      }
      await loadAttachments();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) uploadFile(file);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) uploadFile(file);
    e.target.value = '';
  };

  const handleDelete = async (id, nombre) => {
    if (!window.confirm(`¿Borrar "${nombre}"?`)) return;
    try {
      const headers = await authHeader();
      const res = await fetch(`${apiBaseUrl}/api/attachments/${id}`, { method: 'DELETE', headers });
      if (!res.ok) throw new Error('No se pudo borrar el adjunto');
      await loadAttachments();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
        Documentos adjuntos al informe
      </h3>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>
        NPS, constancias de declaración y otros PDFs que se agregarán al final del informe descargado para este período.
      </p>

      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${dragOver ? 'var(--accent-primary)' : 'rgba(255,255,255,0.15)'}`,
          borderRadius: '8px',
          padding: '2rem',
          textAlign: 'center',
          color: 'var(--text-muted)',
          transition: 'border-color 0.2s',
        }}
      >
        {uploading ? (
          <Loader2 size={24} className="spin" style={{ marginBottom: '0.5rem' }} />
        ) : (
          <Upload size={24} style={{ marginBottom: '0.5rem', opacity: 0.6 }} />
        )}
        <p style={{ margin: '0 0 0.5rem 0' }}>
          {uploading ? 'Subiendo...' : 'Arrastra un PDF aquí, o'}
        </p>
        <label className="btn btn-outline" style={{ cursor: 'pointer', display: 'inline-flex' }}>
          Elegir archivo
          <input type="file" accept="application/pdf" onChange={handleFileSelect} style={{ display: 'none' }} disabled={uploading} />
        </label>
      </div>

      {error && <p style={{ color: '#ef4444', fontSize: '0.85rem', margin: 0 }}>{error}</p>}

      {loading ? (
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Cargando adjuntos...</p>
      ) : attachments.length === 0 ? (
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Sin adjuntos para este período.</p>
      ) : (
        <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {attachments.map((att) => (
            <li key={att.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: 'rgba(255,255,255,0.03)', borderRadius: '6px' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-main)', fontSize: '0.85rem' }}>
                <FileText size={16} />
                {att.nombre_archivo}
              </span>
              <button
                onClick={() => handleDelete(att.id, att.nombre_archivo)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#ef4444', display: 'flex', alignItems: 'center' }}
                title="Borrar"
              >
                <Trash2 size={16} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Import it in `DashboardView.jsx`**

Add to the import block at the top of the file (after `import './DashboardView.css';`):

```jsx
import AttachmentsDropzone from './AttachmentsDropzone';
```

- [ ] **Step 3: Render it at the bottom of the dashboard, admin/accountant only**

Find the closing of the `.bento-grid` div — it is the line that reads exactly:

```jsx
      </div>

    </div>
  );
```

(the `.bento-grid` div's closing tag, followed by the outer container's closing tag). Insert the new block between them, so it reads:

```jsx
      </div>

      {(userRole === 'admin' || userRole === 'accountant') && (
        <AttachmentsDropzone
          clienteId={currentClient.id}
          periodo={selectedPeriodo}
          apiBaseUrl={API_BASE_URL}
        />
      )}

    </div>
  );
```

- [ ] **Step 4: Manual test — admin sees the dropzone**

With `npm run dev` still running (Task 4 Step 4) and the local backend from Task 2 running too, set `VITE_API_URL` to point at the local backend for this test session:

```bash
cd "D:/2.-Quanta/1.- Quanta_sistema/frontend"
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
```

Log in as `admin@quanta.pe`, select a client, open the Dashboard tab, and scroll to the bottom. Expected: the "Documentos adjuntos al informe" panel is visible below the grid, initially showing "Sin adjuntos para este período." (or "Cargando adjuntos..." briefly).

- [ ] **Step 5: Manual test — upload, list, delete round-trip in the browser**

Click "Elegir archivo", pick any real PDF from disk. Expected: "Subiendo..." briefly, then the file appears in the list below the drop zone. Click the trash icon next to it, confirm the browser's confirm dialog. Expected: the file disappears from the list.

- [ ] **Step 6: Manual test — client role does not see the dropzone**

Log in as a `client`-role test account, open their Dashboard. Expected: the report download button still works exactly as before, and there is no drop-zone panel anywhere on the page.

- [ ] **Step 7: Remove the local test override**

```bash
cd "D:/2.-Quanta/1.- Quanta_sistema/frontend"
rm .env.local
```

(This file is local-only and must not be committed — confirm it's git-ignored or simply not staged in the next step.)

- [ ] **Step 8: Commit**

```bash
cd "D:/2.-Quanta/1.- Quanta_sistema"
git add frontend/src/components/AttachmentsDropzone.jsx frontend/src/components/DashboardView.jsx
git status --short
```

Confirm `frontend/.env.local` does NOT appear in the output before committing. Then:

```bash
git commit -m "Add AttachmentsDropzone, mounted at the bottom of the Dashboard for admin/accountant"
```

---

### Task 6: Deploy and smoke-test in production

**Files:** none (deployment only)

**Interfaces:** none — this task verifies the previous five tasks' combined behavior on Railway + Vercel.

- [ ] **Step 1: Push to `main`**

```bash
cd "D:/2.-Quanta/1.- Quanta_sistema"
git push origin main
```

This triggers a Railway redeploy of the backend and a Vercel redeploy of `quanta-app` (frontend).

- [ ] **Step 2: Confirm both deploys succeed**

Poll Railway (`describe-environment` on project `7af1c72c-1ab9-4159-88dd-23a8604b9810`, service `5e7ebd42-79e3-4524-9207-ae3d22cbeb57`) and Vercel (`get_project` on `prj_XdIiv8u6h7PVeIRfhpwkrUBj317O`) until both `latestDeployment.status` / `readyState` read `SUCCESS` / `READY`.

- [ ] **Step 3: Smoke-test the deployed upload endpoint**

Repeat Task 2 Step 6 against the production URL instead of `localhost:8000`:

```bash
curl -s -X POST "https://quanta-production-07d7.up.railway.app/api/attachments/upload" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@/tmp/test-attachment.pdf" \
  -F "cliente_id=<CLIENTE_ID>" \
  -F "periodo=202608"
```

Expected: same success response as the local test. Delete it afterward via `DELETE /api/attachments/<id>` against the same production URL.

- [ ] **Step 4: Smoke-test the live Dashboard**

Open the production frontend URL, log in as `admin@quanta.pe`, open any client's Dashboard, and confirm the "Documentos adjuntos al informe" panel appears and the upload/list/delete round-trip from Task 5 Step 5 still works against production.

- [ ] **Step 5: Confirm nothing else regressed**

Click "Descargar Informe PDF" for a client+periodo with no attachments and confirm it downloads exactly as it did before this feature existed.
