-- Create a view that aggregates purchases and sales per month and per client
CREATE OR REPLACE VIEW v_resumen_mensual AS
SELECT 
    cliente,
    periodo,
    SUBSTRING(periodo FROM 1 FOR 4) AS anio,
    SUBSTRING(periodo FROM 5 FOR 2) AS mes,
    COUNT(CASE WHEN libro = 'COMPRAS' THEN 1 END) AS cantidad_compras,
    SUM(CASE WHEN libro = 'COMPRAS' THEN total_cp ELSE 0 END) AS total_compras,
    COUNT(CASE WHEN libro = 'VENTAS' THEN 1 END) AS cantidad_ventas,
    SUM(CASE WHEN libro = 'VENTAS' THEN total_cp ELSE 0 END) AS total_ventas,
    SUM(CASE WHEN libro = 'VENTAS' THEN total_cp ELSE 0 END) - SUM(CASE WHEN libro = 'COMPRAS' THEN total_cp ELSE 0 END) AS utilidad_bruta
FROM v_libro_unificado
GROUP BY cliente, periodo
ORDER BY cliente, periodo DESC;

COMMENT ON VIEW v_resumen_mensual IS 'Resumen mensual de compras vs ventas para visualización estilo gráfico en Supabase Studio';
