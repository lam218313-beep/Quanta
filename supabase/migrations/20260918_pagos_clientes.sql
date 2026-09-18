-- ═══════════════════════════════════════════════════════════════════
-- Quanta V2 — Migration: Pagos de Clientes (Gestor de Pagos)
-- Backs the existing "Gestor de Pagos" UI in ClientesView.jsx, which
-- already implements auto-generation of monthly records, PAGADO/PENDIENTE
-- toggling, and receipt uploads — this migration only supplies the
-- table, indexes and access policies it was already written against.
-- ═══════════════════════════════════════════════════════════════════

-- 1. Payments table
CREATE TABLE IF NOT EXISTS pagos_clientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    periodo TEXT NOT NULL, -- display string, e.g. 'Septiembre 2026' (matches frontend's getMesesPasados())
    monto NUMERIC(10,2) NOT NULL DEFAULT 150.00,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE'
        CHECK (estado IN ('PENDIENTE', 'PAGADO')),
    fecha_pago DATE,
    ruta_comprobante TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (cliente_id, periodo)
);

CREATE INDEX IF NOT EXISTS idx_pagos_clientes_cliente ON pagos_clientes(cliente_id);
CREATE INDEX IF NOT EXISTS idx_pagos_clientes_estado ON pagos_clientes(estado);

COMMENT ON TABLE pagos_clientes IS 'Registro mensual de pagos del servicio contable por cliente. Gestionado desde ClientesView > Gestor de Pagos.';

-- 2. RLS — this table is billing data the frontend writes to directly from
-- the browser (no backend endpoint in between), so RLS is the real
-- enforcement boundary. Only admin/accountant may read or write; a
-- 'client' role must never be able to mark their own invoice as paid.
ALTER TABLE pagos_clientes ENABLE ROW LEVEL SECURITY;

CREATE POLICY staff_manage_pagos ON pagos_clientes
    FOR ALL USING (get_user_role() IN ('admin', 'accountant'));

-- 3. Storage bucket for uploaded payment receipts.
-- Public read (the frontend uses getPublicUrl, not signed URLs) but only
-- admin/accountant may upload, replace or delete files.
INSERT INTO storage.buckets (id, name, public)
VALUES ('comprobantes_pagos', 'comprobantes_pagos', true)
ON CONFLICT (id) DO NOTHING;

CREATE POLICY comprobantes_public_read ON storage.objects
    FOR SELECT USING (bucket_id = 'comprobantes_pagos');

CREATE POLICY comprobantes_staff_write ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'comprobantes_pagos'
        AND get_user_role() IN ('admin', 'accountant')
    );

CREATE POLICY comprobantes_staff_update ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'comprobantes_pagos'
        AND get_user_role() IN ('admin', 'accountant')
    );

CREATE POLICY comprobantes_staff_delete ON storage.objects
    FOR DELETE USING (
        bucket_id = 'comprobantes_pagos'
        AND get_user_role() IN ('admin', 'accountant')
    );
