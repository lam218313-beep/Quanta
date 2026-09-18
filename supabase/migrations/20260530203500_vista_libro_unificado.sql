-- =============================================================
-- Vista unificada: Libro de Compras y Ventas en una sola tabla
-- Filtrable por periodo (rango de años/meses)
-- =============================================================

CREATE VIEW v_libro_unificado AS

-- Bloque COMPRAS
SELECT
    'COMPRAS' AS libro,
    c.ruc,
    c.razon_social AS cliente,
    p.periodo,
    p.car_sunat,
    p.fecha_emision,
    p.fecha_vcto_pago,
    p.tipo_cp_doc,
    p.serie_cdp,
    p.nro_cp,
    p.tipo_doc_identidad,
    p.nro_doc_identidad AS ruc_tercero,
    p.razon_social AS nombre_tercero,
    p.bi_gravado_dg AS base_imponible,
    p.igv_ipm_dg AS igv,
    p.total_cp,
    p.moneda,
    p.tipo_cambio,
    p.descripcion_comprobante,
    p.estado_enriquecimiento,
    p.detraccion,
    p.created_at
FROM sire_preliminar_compras p
JOIN clientes c ON c.id = p.cliente_id

UNION ALL

-- Bloque VENTAS
SELECT
    'VENTAS' AS libro,
    c.ruc,
    c.razon_social AS cliente,
    v.periodo,
    v.car_sunat,
    v.fecha_emision,
    v.fecha_vcto_pago,
    v.tipo_cp_doc,
    v.serie_cdp,
    v.nro_cp,
    v.tipo_doc_identidad,
    v.nro_doc_identidad AS ruc_tercero,
    v.razon_social AS nombre_tercero,
    v.bi_gravada AS base_imponible,
    v.igv_ipm AS igv,
    v.total_cp,
    v.moneda,
    v.tipo_cambio,
    v.descripcion_comprobante,
    v.estado_enriquecimiento,
    NULL AS detraccion,
    v.created_at
FROM sire_preliminar_ventas v
JOIN clientes c ON c.id = v.cliente_id;

COMMENT ON VIEW v_libro_unificado IS 'Vista unificada de compras y ventas, filtrable por periodo. Ej: SELECT * FROM v_libro_unificado WHERE periodo BETWEEN 202501 AND 202512';
