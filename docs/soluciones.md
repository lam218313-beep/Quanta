# 🛠️ Soluciones — Contax Dev Environment

## Error: `exec /usr/bin/tini: input/output error` al ejecutar `npx supabase start`

**Fecha:** 2026-06-30  
**Entorno:** Windows + Docker Desktop + WSL2  
**CLI:** Supabase CLI 2.108.0

---

### ❌ Síntoma

Al ejecutar `npx supabase start`, el proceso fallaba con:

```
Starting database...
Initialising schema...
Stopping containers...
error running container: exit 255
```

Y con `--debug`:

```
exec /usr/bin/tini: input/output error
```

---

### 🔍 Causa Raíz

El componente **Analytics** (`[analytics]` en `config.toml`) requiere que el daemon de Docker esté expuesto en `tcp://localhost:2375` para funcionar en Windows. Esta opción **no está habilitada por defecto** en Docker Desktop.

Sin el puerto TCP expuesto, el contenedor de inicialización del schema falla al intentar ejecutar su proceso `tini`, resultando en el error de I/O.

La CLI muestra el warning (visible solo con `--debug` o ejecutando el `.exe` directo):

```
WARNING: Analytics on Windows requires Docker daemon exposed on tcp://localhost:2375.
See https://supabase.com/docs/guides/local-development/cli/getting-started
```

---

### ✅ Solución Aplicada

**Opción A — Deshabilitar Analytics** *(solución rápida, aplicada)*

En `supabase/config.toml`, cambiar:

```toml
[analytics]
enabled = false   # ← era true
```

**Opción B — Habilitar Docker TCP** *(si necesitas Analytics)*

1. Abrir **Docker Desktop → Settings → General**
2. Activar ✅ **"Expose daemon on tcp://localhost:2375 without TLS"**
3. Reiniciar Docker Desktop
4. Cambiar `analytics.enabled = true` en `config.toml`

---

### 📝 Cambios adicionales realizados

- `supabase/config.toml`: Renombrado `[inbucket]` → `[local_smtp]` (sección deprecada)
- `supabase/seed.sql`: Creado archivo vacío requerido por `[db.seed] sql_paths = ["./seed.sql"]`

---

### 🔗 Referencias

- [Supabase CLI en Windows](https://supabase.com/docs/guides/local-development/cli/getting-started?platform=windows)
- Issue relacionado: `exec /usr/bin/tini: input/output error` en Docker Desktop/WSL2

