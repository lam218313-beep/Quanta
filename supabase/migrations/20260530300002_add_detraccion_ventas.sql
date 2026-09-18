-- Agrega columna detraccion a sire_preliminar_ventas (ya existe en compras)
ALTER TABLE sire_preliminar_ventas
  ADD COLUMN IF NOT EXISTS detraccion VARCHAR(5) DEFAULT 'NO';

COMMENT ON COLUMN sire_preliminar_ventas.detraccion IS 'Indica si el comprobante de venta aplica detracción (SI/NO), extraído del XML UBL';
