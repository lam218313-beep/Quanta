-- Crear la tabla unificada de control de archivos físicos (XML/PDF)
CREATE TABLE sire_comprobantes_fisicos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    periodo VARCHAR(6) NOT NULL,
    tipo_libro VARCHAR(10) NOT NULL CHECK (tipo_libro IN ('COMPRAS', 'VENTAS')),
    
    -- Trazabilidad exacta hacia la data contable (Solo una estará llena)
    preliminar_compra_id UUID REFERENCES sire_preliminar_compras(id) ON DELETE CASCADE,
    preliminar_venta_id UUID REFERENCES sire_preliminar_ventas(id) ON DELETE CASCADE,
    
    -- Llaves de búsqueda exactas para el bot en el portal SOL
    ruc_tercero VARCHAR(15) NOT NULL,
    tipo_cp VARCHAR(2) NOT NULL,
    serie VARCHAR(10) NOT NULL,
    numero VARCHAR(50) NOT NULL,
    
    -- Máquina de estados para Playwright
    estado_xml VARCHAR(20) DEFAULT 'PENDIENTE' CHECK (estado_xml IN ('PENDIENTE', 'DESCARGADO', 'ERROR', 'NO_EXISTE', 'NO_DESCARGABLE')),
    estado_pdf VARCHAR(20) DEFAULT 'PENDIENTE' CHECK (estado_pdf IN ('PENDIENTE', 'DESCARGADO', 'ERROR', 'NO_EXISTE', 'NO_DESCARGABLE')),
    
    -- Rutas de almacenamiento local en tu PC
    ruta_xml TEXT,
    ruta_pdf TEXT,
    
    -- Control de resiliencia
    reintentos INT DEFAULT 0,
    error_log TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índice crítico para que el Bot encuentre instantáneamente qué le falta descargar
CREATE INDEX idx_comprobantes_pendientes ON sire_comprobantes_fisicos (cliente_id, periodo, estado_xml, estado_pdf);

-- Índice único para evitar duplicar facturas en la cola de descarga
CREATE UNIQUE INDEX idx_comprobante_unico ON sire_comprobantes_fisicos (cliente_id, periodo, tipo_libro, ruc_tercero, tipo_cp, serie, numero);

COMMENT ON TABLE sire_comprobantes_fisicos IS 'Cola de trabajo RPA e inventario local de XML/PDF';
