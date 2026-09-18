ALTER TABLE clientes
ADD COLUMN IF NOT EXISTS rubro VARCHAR(100) DEFAULT 'empresa comercial general';
