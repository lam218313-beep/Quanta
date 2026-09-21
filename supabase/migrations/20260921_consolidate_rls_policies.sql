-- Consolidates the "multiple permissive policies" advisor warnings (~100
-- findings) on clientes, sire_preliminar_compras, sire_preliminar_ventas,
-- sire_comprobantes_fisicos, user_profiles, and client_attachments.
--
-- Each of these tables had the SAME shape: an admin_all_* (FOR ALL) policy,
-- an accountant_assigned_* (FOR ALL) policy, and a client_own_* (FOR SELECT)
-- policy - meaning up to 3 permissive policies get evaluated per SELECT and
-- 2 per INSERT/UPDATE/DELETE, which Postgres must OR together at runtime.
-- Replaced here with exactly one policy per (table, action), each combining
-- the same conditions with OR - identical access, zero policy overlap.
--
-- Verified before applying in production (via SET LOCAL role=authenticated +
-- request.jwt.claims) that a client account sees only its own rows and the
-- admin account still sees everything, both before and after this change.

-- ── clientes ──────────────────────────────────────────────────────
DROP POLICY IF EXISTS admin_all_clientes ON public.clientes;
DROP POLICY IF EXISTS accountant_assigned_clientes ON public.clientes;
DROP POLICY IF EXISTS client_own_clientes ON public.clientes;

CREATE POLICY clientes_select ON public.clientes FOR SELECT USING (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND id IN (SELECT get_user_cliente_ids()))
    OR id IN (SELECT get_user_cliente_ids())
);
CREATE POLICY clientes_insert ON public.clientes FOR INSERT WITH CHECK (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND id IN (SELECT get_user_cliente_ids()))
);
CREATE POLICY clientes_update ON public.clientes FOR UPDATE USING (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND id IN (SELECT get_user_cliente_ids()))
) WITH CHECK (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND id IN (SELECT get_user_cliente_ids()))
);
CREATE POLICY clientes_delete ON public.clientes FOR DELETE USING (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND id IN (SELECT get_user_cliente_ids()))
);

-- ── sire_preliminar_compras ──────────────────────────────────────
DROP POLICY IF EXISTS admin_all_compras ON public.sire_preliminar_compras;
DROP POLICY IF EXISTS accountant_assigned_compras ON public.sire_preliminar_compras;
DROP POLICY IF EXISTS client_own_compras ON public.sire_preliminar_compras;

CREATE POLICY compras_select ON public.sire_preliminar_compras FOR SELECT USING (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
    OR cliente_id IN (SELECT get_user_cliente_ids())
);
CREATE POLICY compras_insert ON public.sire_preliminar_compras FOR INSERT WITH CHECK (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
);
CREATE POLICY compras_update ON public.sire_preliminar_compras FOR UPDATE USING (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
) WITH CHECK (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
);
CREATE POLICY compras_delete ON public.sire_preliminar_compras FOR DELETE USING (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
);

-- ── sire_preliminar_ventas ───────────────────────────────────────
DROP POLICY IF EXISTS admin_all_ventas ON public.sire_preliminar_ventas;
DROP POLICY IF EXISTS accountant_assigned_ventas ON public.sire_preliminar_ventas;
DROP POLICY IF EXISTS client_own_ventas ON public.sire_preliminar_ventas;

CREATE POLICY ventas_select ON public.sire_preliminar_ventas FOR SELECT USING (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
    OR cliente_id IN (SELECT get_user_cliente_ids())
);
CREATE POLICY ventas_insert ON public.sire_preliminar_ventas FOR INSERT WITH CHECK (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
);
CREATE POLICY ventas_update ON public.sire_preliminar_ventas FOR UPDATE USING (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
) WITH CHECK (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
);
CREATE POLICY ventas_delete ON public.sire_preliminar_ventas FOR DELETE USING (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
);

-- ── sire_comprobantes_fisicos ────────────────────────────────────
DROP POLICY IF EXISTS admin_all_fisicos ON public.sire_comprobantes_fisicos;
DROP POLICY IF EXISTS accountant_assigned_fisicos ON public.sire_comprobantes_fisicos;
DROP POLICY IF EXISTS client_own_fisicos ON public.sire_comprobantes_fisicos;

CREATE POLICY fisicos_select ON public.sire_comprobantes_fisicos FOR SELECT USING (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
    OR cliente_id IN (SELECT get_user_cliente_ids())
);
CREATE POLICY fisicos_insert ON public.sire_comprobantes_fisicos FOR INSERT WITH CHECK (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
);
CREATE POLICY fisicos_update ON public.sire_comprobantes_fisicos FOR UPDATE USING (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
) WITH CHECK (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
);
CREATE POLICY fisicos_delete ON public.sire_comprobantes_fisicos FOR DELETE USING (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
);

-- ── client_attachments ───────────────────────────────────────────
DROP POLICY IF EXISTS admin_all_attachments ON public.client_attachments;
DROP POLICY IF EXISTS accountant_assigned_attachments ON public.client_attachments;
DROP POLICY IF EXISTS client_own_attachments ON public.client_attachments;

CREATE POLICY attachments_select ON public.client_attachments FOR SELECT USING (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
    OR cliente_id IN (SELECT get_user_cliente_ids())
);
CREATE POLICY attachments_insert ON public.client_attachments FOR INSERT WITH CHECK (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
);
CREATE POLICY attachments_update ON public.client_attachments FOR UPDATE USING (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
) WITH CHECK (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
);
CREATE POLICY attachments_delete ON public.client_attachments FOR DELETE USING (
    get_user_role() = 'admin'
    OR (get_user_role() = 'accountant' AND cliente_id IN (SELECT get_user_cliente_ids()))
);

-- ── user_profiles (2-policy shape: admin_manage_users + user_read_own) ──
DROP POLICY IF EXISTS admin_manage_users ON public.user_profiles;
DROP POLICY IF EXISTS user_read_own ON public.user_profiles;

CREATE POLICY user_profiles_select ON public.user_profiles FOR SELECT USING (
    get_user_role() = 'admin' OR id = auth.uid()
);
CREATE POLICY user_profiles_insert ON public.user_profiles FOR INSERT WITH CHECK (
    get_user_role() = 'admin'
);
CREATE POLICY user_profiles_update ON public.user_profiles FOR UPDATE USING (
    get_user_role() = 'admin'
) WITH CHECK (
    get_user_role() = 'admin'
);
CREATE POLICY user_profiles_delete ON public.user_profiles FOR DELETE USING (
    get_user_role() = 'admin'
);

-- ── Follow-up findings from re-running the advisor after the above ──────
-- client_attachments (new table from yesterday) was missing an index on
-- its subido_por FK; user_profiles_select re-evaluated auth.uid() per row
-- instead of once (the standard Supabase RLS perf pattern).
CREATE INDEX IF NOT EXISTS idx_client_attachments_subido_por
    ON public.client_attachments (subido_por);

DROP POLICY IF EXISTS user_profiles_select ON public.user_profiles;
CREATE POLICY user_profiles_select ON public.user_profiles FOR SELECT USING (
    get_user_role() = 'admin' OR id = (SELECT auth.uid())
);
