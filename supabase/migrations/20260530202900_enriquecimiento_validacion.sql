-- =============================================================
-- Migración: Parámetros de seguridad para enriquecimiento
-- =============================================================

-- Agregar columna de estado de enriquecimiento a compras
ALTER TABLE sire_preliminar_compras 
  ADD COLUMN estado_enriquecimiento VARCHAR(15) DEFAULT 'PENDIENTE' 
  CHECK (estado_enriquecimiento IN ('PENDIENTE','COMPLETO','PARCIAL','ERROR'));

-- Agregar columna de estado de enriquecimiento a ventas
ALTER TABLE sire_preliminar_ventas 
  ADD COLUMN estado_enriquecimiento VARCHAR(15) DEFAULT 'PENDIENTE' 
  CHECK (estado_enriquecimiento IN ('PENDIENTE','COMPLETO','PARCIAL','ERROR'));

-- Índices para filtrar rápidamente las facturas pendientes de enriquecimiento
CREATE INDEX idx_compras_enriq_pendiente 
  ON sire_preliminar_compras (cliente_id, periodo) 
  WHERE estado_enriquecimiento != 'COMPLETO';

CREATE INDEX idx_ventas_enriq_pendiente 
  ON sire_preliminar_ventas (cliente_id, periodo) 
  WHERE estado_enriquecimiento != 'COMPLETO';

-- =============================================================
-- Vista: Dashboard de completitud por cliente / periodo / libro
-- =============================================================
CREATE VIEW v_completitud_enriquecimiento AS

-- Bloque COMPRAS
SELECT 
    c.ruc,
    c.razon_social,
    p.periodo,
    'COMPRAS' AS libro,
    COUNT(*) AS total_facturas,
    COUNT(p.descripcion_comprobante) AS enriquecidas,
    COUNT(*) - COUNT(p.descripcion_comprobante) AS pendientes,
    ROUND(COUNT(p.descripcion_comprobante)::numeric / NULLIF(COUNT(*), 0) * 100, 1) AS pct_completitud,
    COUNT(*) FILTER (WHERE p.estado_enriquecimiento = 'ERROR') AS con_error
FROM sire_preliminar_compras p
JOIN clientes c ON c.id = p.cliente_id
GROUP BY c.ruc, c.razon_social, p.periodo

UNION ALL

-- Bloque VENTAS
SELECT 
    c.ruc,
    c.razon_social,
    v.periodo,
    'VENTAS' AS libro,
    COUNT(*) AS total_facturas,
    COUNT(v.descripcion_comprobante) AS enriquecidas,
    COUNT(*) - COUNT(v.descripcion_comprobante) AS pendientes,
    ROUND(COUNT(v.descripcion_comprobante)::numeric / NULLIF(COUNT(*), 0) * 100, 1) AS pct_completitud,
    COUNT(*) FILTER (WHERE v.estado_enriquecimiento = 'ERROR') AS con_error
FROM sire_preliminar_ventas v
JOIN clientes c ON c.id = v.cliente_id
GROUP BY c.ruc, c.razon_social, v.periodo;

COMMENT ON VIEW v_completitud_enriquecimiento IS 'Dashboard de seguridad: muestra % de facturas enriquecidas por cliente, periodo y libro';
