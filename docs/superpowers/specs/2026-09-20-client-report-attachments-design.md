# Adjuntos PDF en el Informe del Dashboard

- **Fecha:** 2026-09-20
- **Estado:** Aprobado, pendiente de implementación

## Propósito

Hoy el Dashboard (`DashboardView.jsx`) genera un informe financiero PDF a
demanda (`POST /api/pdf/report`) a partir de datos vivos de `v_libro_unificado`.
Ese es el único PDF que tanto el admin/contador como el cliente descargan con
el botón "Descargar Informe PDF".

El admin (o contador) necesita poder subir documentos adicionales por
cliente y período — NPS, constancias de declaración, y similares — que se
agreguen al final de ese mismo PDF, de modo que cuando el cliente lo
descargue reciba un solo archivo con el informe más esos documentos anexos.

## Alcance de las decisiones ya tomadas

- Los adjuntos quedan ligados a **cliente + período** (no a un cliente para
  siempre): subir un PDF para agosto de un cliente solo aparece cuando se
  descarga el informe de ese cliente en agosto.
- Pueden subir adjuntos los roles **admin y accountant** (no `client`).
- La entrega es **un único PDF fusionado** (no archivos separados): el
  informe generado + las páginas de cada adjunto, en orden de subida.
- El admin/accountant puede **agregar y eliminar** adjuntos antes de que el
  cliente los descargue.

## Modelo de datos

Tabla nueva `client_attachments`, mismo estilo que el resto del esquema
(`clientes`, `sire_comprobantes_fisicos`):

```sql
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

CREATE POLICY admin_all_attachments ON public.client_attachments
    FOR ALL USING (get_user_role() = 'admin');

CREATE POLICY accountant_assigned_attachments ON public.client_attachments
    FOR ALL USING (
        get_user_role() = 'accountant'
        AND cliente_id IN (SELECT get_user_cliente_ids())
    );

CREATE POLICY client_own_attachments ON public.client_attachments
    FOR SELECT USING (cliente_id IN (SELECT get_user_cliente_ids()));
```

Nota: estas políticas siguen exactamente el mismo patrón (y la misma
limitación ya conocida de `get_user_cliente_ids()`) que ya tiene `clientes`
— no se corrige aquí ese diseño más amplio de "clientes asignados a un
contador", queda fuera de alcance. El backend igual usa la service_role key
(bypassa RLS), así que estas políticas son defensa en profundidad para el
día en que algo consulte esta tabla directo desde el frontend, no la única
protección real.

## Almacenamiento

Bucket privado nuevo, mismo patrón que `comprobantes-fisicos`:

```sql
INSERT INTO storage.buckets (id, name, public)
VALUES ('client-attachments', 'client-attachments', false)
ON CONFLICT (id) DO NOTHING;
```

Path dentro del bucket: `{cliente_id}/{periodo}/{uuid}-{nombre_archivo}`.
Solo el backend (service_role) lee/escribe; no hace falta política de
`storage.objects` porque no hay URL pública ni acceso directo desde el
cliente.

## Backend

Router nuevo `app/brain/routes/attachments.py`, montado en `app/api.py`
junto a los demás routers.

- `POST /api/attachments/upload` — `Depends(require_role("admin", "accountant"))`.
  Recibe `multipart/form-data`: `file` (PDF), `cliente_id`, `periodo`.
  Valida extensión/content-type `.pdf` y tamaño ≤ 15MB. Sube a Storage,
  inserta la fila (con `subido_por = user.user_id`), devuelve el registro
  creado.
- `GET /api/attachments/{cliente_id}/{periodo}` — mismo rol. Lista los
  adjuntos existentes (para pintar la lista en la UI), ordenados por
  `created_at`.
- `DELETE /api/attachments/{id}` — mismo rol. Borra el objeto de Storage y
  la fila; 404 si no existe.

Modificación a `app/brain/routes/pdf.py` (`generate_report_pdf`): después de
generar el PDF del informe con `generate_financial_report_pdf` (sin cambios
en esa función ni en su plantilla), si `client_attachments` tiene filas para
`(cliente_id, periodo)`:

1. Abrir el PDF generado con PyMuPDF (`fitz.open(output_path)`) — ya está en
   `requirements.txt`, no se agrega ninguna dependencia nueva.
2. Por cada adjunto, en orden de `created_at`: descargarlo de Storage,
   abrirlo con `fitz.open(stream=contenido, filetype="pdf")`, y pegarlo al
   final con `informe.insert_pdf(adjunto)`.
3. Si un adjunto individual falla al descargarse o no es un PDF válido, se
   omite (se loguea) y se sigue con los demás — nunca debe romper la
   descarga del informe base.
4. Guardar el PDF combinado sobre `output_path` y servirlo como hoy
   (`FileResponse`).

## Frontend

- `App.jsx` pasa una prop nueva `userRole` a `<DashboardView>` (hoy no se la
  pasa; el estado `userRole` ya existe en `App.jsx`).
- Componente nuevo `frontend/src/components/AttachmentsDropzone.jsx`,
  montado al final de `DashboardView.jsx`, renderizado solo si
  `userRole === 'admin' || userRole === 'accountant'`.
  - Zona de drag-and-drop + `<input type="file" accept="application/pdf">`
    como alternativa al arrastrar.
  - Valida `.pdf` en el cliente antes de subir (mensaje de error si no).
  - Al soltar/seleccionar, sube vía `POST /api/attachments/upload` con el
    `access_token` de la sesión de Supabase en el header `Authorization`.
  - Debajo de la zona, lista los adjuntos del `currentClient` +
    `selectedPeriodo` activos (vía `GET`), cada uno con nombre y un botón
    de borrar (confirma con un diálogo simple antes de `DELETE`).
  - Se recarga la lista cuando cambia `currentClient` o `selectedPeriodo`,
    igual que ya hace `loadDashboardData()`.
- El rol `client` no ve este componente en absoluto — su único cambio
  observable es que el PDF que ya descarga con el botón existente puede
  traer páginas extra al final.

## Manejo de errores y bordes

- Solo `.pdf` (validado en frontend y backend por extensión/content-type).
- Límite de tamaño 15MB por archivo.
- Si la generación del informe base falla, no se intenta la fusión (sin
  cambio de comportamiento actual).
- Si falla la fusión de UN adjunto puntual, se sirve igual el informe con
  los demás adjuntos que sí funcionaron (nunca bloquea la descarga
  completa).
- Borrar un adjunto es inmediato (no hay papelera/soft-delete).

## Testing

- Backend: subir un PDF válido y confirmar la fila + el objeto en Storage;
  subir un archivo no-PDF y confirmar 400; borrar un adjunto y confirmar
  que desaparece de Storage y de la tabla; pedir el informe con y sin
  adjuntos y confirmar el conteo de páginas del PDF resultante.
- Frontend: verificar en el navegador que la zona de drop solo aparece para
  admin/accountant, que la lista se actualiza al cambiar de cliente/período,
  y que el botón de descarga del cliente (probado como rol `client`) sigue
  funcionando igual cuando no hay adjuntos.

## Fuera de alcance

- Reordenar adjuntos por drag-and-drop (se fusionan en orden de subida).
- Categorías/etiquetas por tipo de documento (NPS vs. constancia, etc.) —
  el nombre del archivo alcanza para esta primera versión.
- Corregir el mecanismo más amplio de "clientes asignados a un contador"
  (`get_user_cliente_ids()` para rol `accountant`), que ya tenía esta
  limitación antes de este cambio.
