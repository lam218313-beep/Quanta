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
