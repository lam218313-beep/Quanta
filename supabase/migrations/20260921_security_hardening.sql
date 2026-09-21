-- Security/perf hardening flagged by the Supabase advisor on day one but
-- not yet applied:
--
-- 1. v_libro_unificado, v_resumen_mensual, v_completitud_enriquecimiento
--    were SECURITY DEFINER (Postgres default for views): they ran with the
--    view CREATOR's privileges, bypassing RLS on the underlying tables for
--    EVERY querying user. DashboardView.jsx queries v_libro_unificado
--    directly from the frontend as the logged-in user - this meant any
--    'client' role user could see every other client's financial data.
--    security_invoker = true makes each view enforce RLS as the querying
--    user, matching what the 3-policy pattern on the base tables already
--    intends.
ALTER VIEW public.v_libro_unificado SET (security_invoker = true);
ALTER VIEW public.v_resumen_mensual SET (security_invoker = true);
ALTER VIEW public.v_completitud_enriquecimiento SET (security_invoker = true);

-- 2. get_user_role() / get_user_cliente_ids() had no search_path pinned,
--    so they resolved unqualified table names (user_profiles) via
--    whatever search_path was active for the caller - a role with
--    CREATE privilege on a schema earlier in that path could shadow
--    user_profiles with a malicious table of the same name. Both already
--    use public.user_profiles implicitly; pin the resolution explicitly.
CREATE OR REPLACE FUNCTION public.get_user_role()
 RETURNS text
 LANGUAGE sql
 SECURITY DEFINER
 SET search_path = public
AS $function$
    SELECT COALESCE(
        (SELECT role FROM user_profiles WHERE id = auth.uid()),
        'anonymous'
    );
$function$;

CREATE OR REPLACE FUNCTION public.get_user_cliente_ids()
 RETURNS SETOF uuid
 LANGUAGE sql
 SECURITY DEFINER
 SET search_path = public
AS $function$
    SELECT cliente_id FROM user_profiles
    WHERE id = auth.uid()
    AND cliente_id IS NOT NULL;
$function$;

-- 3. sire_comprobantes_fisicos has two foreign keys with no covering
--    index (preliminar_compra_id, preliminar_venta_id), which the
--    advisor flagged as suboptimal for the frequent joins/deletes.
CREATE INDEX IF NOT EXISTS idx_fisicos_preliminar_compra_id
    ON public.sire_comprobantes_fisicos (preliminar_compra_id);
CREATE INDEX IF NOT EXISTS idx_fisicos_preliminar_venta_id
    ON public.sire_comprobantes_fisicos (preliminar_venta_id);
