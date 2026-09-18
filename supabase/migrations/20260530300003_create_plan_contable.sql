-- Tabla del Plan Contable General para Empresas (PCGE)
CREATE TABLE IF NOT EXISTS plan_contable (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    nivel INT NOT NULL  -- 2=cuenta mayor, 3=subcuenta, 4+=análitico
);

CREATE INDEX IF NOT EXISTS idx_plan_contable_nivel ON plan_contable (nivel);
CREATE INDEX IF NOT EXISTS idx_plan_contable_codigo ON plan_contable (codigo);

COMMENT ON TABLE plan_contable IS 'Plan Contable General Empresarial (PCGE) - Perú. Usado por el clasificador IA para asignar cuentas contables.';
