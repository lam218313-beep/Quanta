-- Private bucket for SIRE "Fisicos" XML/PDF downloads (sire_bot_orchestrator.py).
-- Railway's local disk is ephemeral and gets wiped on every deploy, so
-- downloaded comprobantes are persisted here instead. Only the backend
-- (service_role, bypasses RLS) reads/writes it, and files are served through
-- GET /api/bot/comprobante-file/{fisico_id} — never a direct public URL —
-- so no storage.objects RLS policies are required.
--
-- Applied directly via the Supabase Storage API on 2026-09-19 (bucket
-- already exists in production); this file documents that change for the
-- migration history and for reproducing it in another environment.
INSERT INTO storage.buckets (id, name, public)
VALUES ('comprobantes-fisicos', 'comprobantes-fisicos', false)
ON CONFLICT (id) DO NOTHING;
