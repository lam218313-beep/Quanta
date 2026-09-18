-- ═══════════════════════════════════════════════════════════════════
-- Quanta V2 — Migration: User Profiles & Row Level Security
-- ═══════════════════════════════════════════════════════════════════

-- 1. User profiles table (linked to Supabase Auth)
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL DEFAULT 'client'
        CHECK (role IN ('admin', 'accountant', 'client')),
    cliente_id UUID REFERENCES clientes(id) ON DELETE SET NULL,
    nombre TEXT,
    email TEXT UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_profiles_role ON user_profiles(role);
CREATE INDEX IF NOT EXISTS idx_user_profiles_cliente ON user_profiles(cliente_id);

COMMENT ON TABLE user_profiles IS 'Perfiles de usuario vinculados a Supabase Auth. Soporta roles: admin, accountant, client.';

-- 2. Helper function to get the current user's role
CREATE OR REPLACE FUNCTION get_user_role()
RETURNS TEXT AS $$
    SELECT COALESCE(
        (SELECT role FROM user_profiles WHERE id = auth.uid()),
        'anonymous'
    );
$$ LANGUAGE sql SECURITY DEFINER;

-- 3. Helper function to get the current user's cliente_id(s)
CREATE OR REPLACE FUNCTION get_user_cliente_ids()
RETURNS SETOF UUID AS $$
    SELECT cliente_id FROM user_profiles
    WHERE id = auth.uid()
    AND cliente_id IS NOT NULL;
$$ LANGUAGE sql SECURITY DEFINER;

-- 4. Enable RLS on critical tables
ALTER TABLE sire_preliminar_compras ENABLE ROW LEVEL SECURITY;
ALTER TABLE sire_preliminar_ventas ENABLE ROW LEVEL SECURITY;
ALTER TABLE sire_comprobantes_fisicos ENABLE ROW LEVEL SECURITY;
ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;

-- 5. RLS Policies: Admin sees everything
CREATE POLICY admin_all_compras ON sire_preliminar_compras
    FOR ALL USING (get_user_role() = 'admin');

CREATE POLICY admin_all_ventas ON sire_preliminar_ventas
    FOR ALL USING (get_user_role() = 'admin');

CREATE POLICY admin_all_fisicos ON sire_comprobantes_fisicos
    FOR ALL USING (get_user_role() = 'admin');

CREATE POLICY admin_all_clientes ON clientes
    FOR ALL USING (get_user_role() = 'admin');

-- 6. RLS Policies: Client sees only their own data
CREATE POLICY client_own_compras ON sire_preliminar_compras
    FOR SELECT USING (
        cliente_id IN (SELECT get_user_cliente_ids())
    );

CREATE POLICY client_own_ventas ON sire_preliminar_ventas
    FOR SELECT USING (
        cliente_id IN (SELECT get_user_cliente_ids())
    );

CREATE POLICY client_own_fisicos ON sire_comprobantes_fisicos
    FOR SELECT USING (
        cliente_id IN (SELECT get_user_cliente_ids())
    );

CREATE POLICY client_own_clientes ON clientes
    FOR SELECT USING (
        id IN (SELECT get_user_cliente_ids())
    );

-- 7. RLS Policies: Accountant sees assigned clients
-- (For now, accountants work the same as clients — they see their assigned cliente_id)
CREATE POLICY accountant_assigned_compras ON sire_preliminar_compras
    FOR ALL USING (
        get_user_role() = 'accountant'
        AND cliente_id IN (SELECT get_user_cliente_ids())
    );

CREATE POLICY accountant_assigned_ventas ON sire_preliminar_ventas
    FOR ALL USING (
        get_user_role() = 'accountant'
        AND cliente_id IN (SELECT get_user_cliente_ids())
    );

CREATE POLICY accountant_assigned_fisicos ON sire_comprobantes_fisicos
    FOR ALL USING (
        get_user_role() = 'accountant'
        AND cliente_id IN (SELECT get_user_cliente_ids())
    );

CREATE POLICY accountant_assigned_clientes ON clientes
    FOR ALL USING (
        get_user_role() = 'accountant'
        AND id IN (SELECT get_user_cliente_ids())
    );

-- 8. Service role bypasses RLS (the backend uses service_role key)
-- This is automatic in Supabase — service_role key bypasses all RLS policies.
-- No additional configuration needed.

-- 9. RLS on user_profiles itself
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY admin_manage_users ON user_profiles
    FOR ALL USING (get_user_role() = 'admin');

CREATE POLICY user_read_own ON user_profiles
    FOR SELECT USING (id = auth.uid());
