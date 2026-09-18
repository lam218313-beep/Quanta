-- Migración: Columnas para la clasificación IA (Fase de Enriquecimiento Contable)

-- Compras
ALTER TABLE sire_preliminar_compras
ADD COLUMN IF NOT EXISTS cuenta_contable VARCHAR(10),
ADD COLUMN IF NOT EXISTS descripcion_cuenta TEXT,
ADD COLUMN IF NOT EXISTS categoria VARCHAR(50);

-- Ventas
ALTER TABLE sire_preliminar_ventas
ADD COLUMN IF NOT EXISTS cuenta_contable VARCHAR(10),
ADD COLUMN IF NOT EXISTS descripcion_cuenta TEXT,
ADD COLUMN IF NOT EXISTS categoria VARCHAR(50);
