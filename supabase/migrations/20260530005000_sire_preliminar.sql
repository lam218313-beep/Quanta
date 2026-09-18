-- Crear tabla espejo de la propuesta del Registro de Compras
CREATE TABLE sire_preliminar_compras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    periodo VARCHAR(6) NOT NULL, -- Ej: '202501'
    
    car_sunat VARCHAR(50) NOT NULL,
    fecha_emision DATE NOT NULL,
    fecha_vcto_pago DATE,
    tipo_cp_doc VARCHAR(2) NOT NULL,
    serie_cdp VARCHAR(10) NOT NULL,
    nro_cp VARCHAR(50) NOT NULL,
    tipo_doc_identidad VARCHAR(2) NOT NULL,
    nro_doc_identidad VARCHAR(15) NOT NULL,
    razon_social TEXT NOT NULL,
    
    bi_gravado_dg NUMERIC(14,2) DEFAULT 0.00,
    igv_ipm_dg NUMERIC(14,2) DEFAULT 0.00,
    bi_gravado_dgng NUMERIC(14,2) DEFAULT 0.00,
    igv_ipm_dgng NUMERIC(14,2) DEFAULT 0.00,
    bi_gravado_dng NUMERIC(14,2) DEFAULT 0.00,
    igv_ipm_dng NUMERIC(14,2) DEFAULT 0.00,
    valor_adq_ng NUMERIC(14,2) DEFAULT 0.00,
    isc NUMERIC(14,2) DEFAULT 0.00,
    icbper NUMERIC(14,2) DEFAULT 0.00,
    otros_trib_cargos NUMERIC(14,2) DEFAULT 0.00,
    total_cp NUMERIC(14,2) DEFAULT 0.00,
    
    moneda VARCHAR(3) NOT NULL,
    tipo_cambio NUMERIC(6,3) DEFAULT 1.000,
    fecha_doc_mod DATE,
    tipo_cp_mod VARCHAR(2),
    serie_cp_mod VARCHAR(10),
    nro_cp_mod VARCHAR(50),
    detraccion VARCHAR(30),
    
    -- Tu campo agregado para la IA
    descripcion_comprobante TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices de alto rendimiento
CREATE INDEX idx_sire_compras_cliente_periodo ON sire_preliminar_compras (cliente_id, periodo);
CREATE UNIQUE INDEX idx_sire_compras_car ON sire_preliminar_compras (car_sunat);

COMMENT ON TABLE sire_preliminar_compras IS 'Espejo de la propuesta RCE de SUNAT con datos consolidados';


----

-- Crear tabla espejo de la propuesta del Registro de Ventas
CREATE TABLE sire_preliminar_ventas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    periodo VARCHAR(6) NOT NULL, -- Ej: '202501'
    
    car_sunat VARCHAR(50) NOT NULL,
    fecha_emision DATE NOT NULL,
    fecha_vcto_pago DATE,
    tipo_cp_doc VARCHAR(2) NOT NULL,
    serie_cdp VARCHAR(10) NOT NULL,
    nro_cp VARCHAR(50) NOT NULL,
    tipo_doc_identidad VARCHAR(2) NOT NULL,
    nro_doc_identidad VARCHAR(15) NOT NULL,
    razon_social TEXT NOT NULL,
    
    valor_fact_exportacion NUMERIC(14,2) DEFAULT 0.00,
    bi_gravada NUMERIC(14,2) DEFAULT 0.00,
    dscto_bi NUMERIC(14,2) DEFAULT 0.00,
    igv_ipm NUMERIC(14,2) DEFAULT 0.00,
    dscto_igv_ipm NUMERIC(14,2) DEFAULT 0.00,
    mto_exonerado NUMERIC(14,2) DEFAULT 0.00,
    mto_inafecto NUMERIC(14,2) DEFAULT 0.00,
    isc NUMERIC(14,2) DEFAULT 0.00,
    bi_grav_ivap NUMERIC(14,2) DEFAULT 0.00,
    ivap NUMERIC(14,2) DEFAULT 0.00,
    icbper NUMERIC(14,2) DEFAULT 0.00,
    otros_tributos NUMERIC(14,2) DEFAULT 0.00,
    total_cp NUMERIC(14,2) DEFAULT 0.00,
    
    moneda VARCHAR(3) NOT NULL,
    tipo_cambio NUMERIC(6,3) DEFAULT 1.000,
    fecha_doc_mod DATE,
    tipo_cp_mod VARCHAR(2),
    serie_cp_mod VARCHAR(10),
    nro_cp_mod VARCHAR(50),
    valor_fob_embarcado NUMERIC(14,2) DEFAULT 0.00,
    
    -- Tu campo agregado para la IA
    descripcion_comprobante TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices de alto rendimiento
CREATE INDEX idx_sire_ventas_cliente_periodo ON sire_preliminar_ventas (cliente_id, periodo);
CREATE UNIQUE INDEX idx_sire_ventas_car ON sire_preliminar_ventas (car_sunat);

COMMENT ON TABLE sire_preliminar_ventas IS 'Espejo de la propuesta RVIE de SUNAT con datos consolidados';
