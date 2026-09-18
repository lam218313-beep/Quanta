-- Crear la tabla maestra de clientes
CREATE TABLE clientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ruc VARCHAR(11) UNIQUE NOT NULL,
    razon_social TEXT NOT NULL,
    usuario_sol VARCHAR(50) NOT NULL,
    clave_sol TEXT NOT NULL,
    client_id_api TEXT,
    client_secret_api TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crear un índice para búsquedas rápidas por RUC
CREATE INDEX idx_clientes_ruc ON clientes(ruc);

-- Crear un índice para filtrar solo los clientes activos
CREATE INDEX idx_clientes_activos ON clientes(activo);

-- Comentario descriptivo para la base de datos
COMMENT ON TABLE clientes IS 'Repositorio central de credenciales SUNAT por cliente';
