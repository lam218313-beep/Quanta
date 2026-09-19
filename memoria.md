# Memoria de sesión — Quanta Contadores

_Actualizado: 2026-09-19 (sesión 2)_

## ⚠️ URL correcta para entrar al sistema (cambió el 2026-09-18)

**No entrar directo a `https://quanta-app-chi.vercel.app/`** — desde el
commit `1ec20ed` ("Add marketing landing site, nested under /app on the
same domain") esa URL da pantalla blanca (404 en los assets JS/CSS)
porque el frontend se compila con `base: '/app/'` en `vite.config.js`,
asumiendo que siempre se sirve detrás del proxy del landing.

**URL correcta: `https://quanta-landing-one.vercel.app/app`** — el
landing (`landing/vercel.json`) reescribe `/app/*` hacia
`quanta-app-chi.vercel.app/*` de forma transparente. Landing = página de
marketing (carpeta `landing/`), app-chi = el sistema real (carpeta
`frontend/`); lo único que cambió es que ahora hay que entrar al sistema
pasando por el dominio del landing, no directo. Decisión confirmada con
el usuario: mantener este esquema (para cuando pongan dominio propio,
sería `<dominio>/app`), no revertir el `base` de Vite.

## Sesión 2026-09-19 (parte 3) — Hueco de la migración a Storage (873 registros)

Al probar el botón de descarga por fila con PROSPERY VIAJES (RUC
`20482345183`, periodo 202607, Julio 2026), salió "El archivo ya no
existe en Supabase Storage". Investigado: **distinto** del bug de los 368
de la parte 2 (ese era de mi corrida local). Este es un hueco real de la
migración original (commit `336d130`, sesión 1): **la migración solo
afectó descargas nuevas hacia adelante — nunca se hizo backfill de los
registros que ya estaban `DESCARGADO` antes del cambio**, y esos seguían
apuntando al disco efímero de Railway (paths tipo
`/app/downloads/xml/.../purchases/xml/archivo.xml`), que ya no existe.

- **Alcance real (auditado con `fetch_all_records`, toda la tabla):
  873 comprobantes en 19 clientes** con `estado_xml`/`estado_pdf =
  DESCARGADO` pero ruta vieja pre-Storage. Los más afectados: ECOSERVIS
  3M (225), DJULIETTE EIRL (124), FERNANDEZ GONZALES ROSELLA (110),
  MAELOS CAR WASH (86), INV. SONRISAS (62), CLINICA DENTAL SANTA INES
  (60), CORPORACION AUTOMOTRIZ TRUX RACING (52), REVIVE FISIOTERAPIA
  (43), OSTEOVIDA (38), MEDRANO GARCIA ADOLFO (19), PROSPERY VIAJES
  (17), y 8 clientes más con menos de 15 cada uno.
- **No recuperable** (a diferencia de los 368 de la parte 2): esos
  archivos nunca se subieron a Storage y el disco de Railway que los
  tenía ya se borró en deploys posteriores. Los datos reales (montos,
  fechas) siguen en `sire_preliminar_compras`/`ventas`; solo el XML/PDF
  físico se perdió.
- **Se resetearon los 873 a `PENDIENTE`** (ruta_xml/ruta_pdf → null,
  reintentos → 0, error_log explicando el motivo) para que se vuelvan a
  descargar de SUNAT y esta vez sí queden en Storage. Verificado:
  0 registros con ruta vieja restantes tras el reset.
- **Pendiente:** falta correr la re-descarga real para estos 19 clientes.
  Como Railway sigue bloqueado por SUNAT (ver diagnóstico de IP en la
  parte 2), esto requeriría correrlo localmente cliente por cliente,
  igual que se hizo con DJULIETTE hoy.
- **Aclaraciones del usuario que quedan como criterio para el futuro:**
  - Los PDFs no importan recuperarlos tal cual — se regeneran solos a
    partir del XML (`pdf_from_xml_service.py`) o el scraper los trae
    directo de SUNAT junto con el XML; no hace falta preservar el PDF
    viejo.
  - Preocupación por saturar el servidor con la descarga automática:
    confirmado en código que **no hay nada corriendo automático hoy**.
    Existe `app/brain/scheduler/daily_sync.py` (pipeline diario con
    throttling de 15s entre clientes) pero está `enabled=False` y **no
    está registrado en ningún lado del backend en ejecución** (ni
    APScheduler ni cron) — es código muerto por ahora. El único disparo
    real es manual, vía el botón, un cliente/periodo a la vez. Dentro de
    una corrida, `download_xml_scraper.py` procesa un comprobante a la
    vez con pausas de 0.3–3s, sin nada en paralelo.

## Sesión 2026-09-19 (parte 2) — Verificación real del pipeline de Storage

1. **Se disparó una autenticación y descarga REAL contra SUNAT** (cliente
   DJULIETTE EIRL, RUC `20611775661`, periodo `202606` COMPRAS) para
   verificar de punta a punta lo que quedó pendiente en la sesión anterior.
   - Frontend en Vercel: `https://quanta-app-chi.vercel.app/`. Backend en
     Railway: `https://quanta-production-07d7.up.railway.app`.
   - La extensión "Claude in Chrome" no conectó en esta sesión, así que se
     probó llamando directo a la API de Railway (`/api/bot/automation-login`,
     `/api/bot/download-fisicos`) en vez de clickear el botón en el navegador.

2. **Diagnóstico del bug del login SUNAT (pendiente desde la sesión 1):**
   el login vía `automation-login` **sigue fallando en Railway** con el
   mismo síntoma de siempre ("Did not reach menu URL in time, or CAPTCHA
   required"). Pero al replicar el mismo código/credenciales **en local**
   (`app/brain/automation_scraper.py`, sin modificarlo), el login **funcionó
   perfecto** y aterrizó en el menú real de SUNAT sin CAPTCHA ni pasos
   extra. Esto descarta credenciales rotas o selectores desactualizados
   como causa — **apunta fuerte a que SUNAT le pone un reto adicional
   (CAPTCHA/verificación) a la IP de datacenter de Railway**, que no
   aparece desde una IP residencial. Sigue sin resolverse (requeriría un
   proxy residencial o similar para Railway), pero ahora hay evidencia
   concreta de la causa en vez de solo sospecha.

3. **Pipeline de Storage verificado de punta a punta con datos reales**
   (esto cierra el pendiente #2 de la sesión 1): se corrió
   `sire_bot_orchestrator.py` en local (mismo código que usa Railway) para
   ese cliente/periodo, con `--limit 5`. Resultado confirmado:
   - Login real a SUNAT ✅, descarga real de 5 comprobantes ✅.
   - Los 5 quedaron `DESCARGADO` en la BD con `ruta_xml`/`ruta_pdf` en
     formato Storage (`{cliente_id}/{periodo}/{tipo_libro}/archivo`), no
     rutas locales.
   - Se descargó uno de los archivos directamente del bucket
     `comprobantes-fisicos` (XML real de 8.4KB, PDF real de 301KB, ambos
     con contenido válido).
   - Se confirmó que el endpoint de producción
     `GET /api/bot/comprobante-file/{id}?tipo=xml` en Railway sirve el
     archivo correctamente desde Storage (200 OK, mismo tamaño).
   - **Conclusión: el pipeline de Storage (commit `336d130`) funciona
     correctamente de punta a punta contra producción real.**

4. **Bug nuevo encontrado (y corregido) en `sync_files.py`
   (`app/brain/db/sync_files.py`):** este script — que se auto-ejecuta al
   final de `orchestrate_xml_downloads()` — **escanea TODA la carpeta
   local `downloads/` sin filtrar por cliente/periodo/RUC**, y por cada
   archivo que hace match por nombre (`{ruc_tercero}-{tipo}-{serie}-{numero}`)
   con un registro no marcado `DESCARGADO`, lo marca `DESCARGADO` pero
   **escribe la ruta local del disco en `ruta_xml`/`ruta_pdf` en vez de
   subirla a Storage**. Esto es inofensivo si corre en Railway justo
   después de una descarga (mismo disco efímero, path válido por unos
   minutos), pero es **peligroso si se corre en una máquina local con una
   carpeta `downloads/` legada** — como pasó en este mismo test: al correr
   el orquestador local (que trae ~4900 archivos viejos de sesiones
   pasadas en disco), `sync_files.py` marcó **368 comprobantes de 16
   clientes distintos** como `DESCARGADO` con rutas de Windows
   (`D:\...\downloads\...`), rutas que el endpoint de producción no puede
   leer (solo sabe leer de Storage) → esos comprobantes se hubieran visto
   con el ✓ verde en el frontend pero la descarga real habría fallado con
   404.
   - **Se corrigió el efecto** (no el código): se subieron esos mismos
     368 archivos reales (sí existían en disco, eran descargas legítimas
     de sesiones anteriores) a Storage con la ruta correcta, y se
     actualizaron las 368 filas en la BD de producción. Verificado:
     0 filas con ruta local restantes tras el fix.
   - **Pendiente de decidir:** `sync_files.py` en sí NO se tocó (mismo
     criterio que con el scraper: no modificar código de automatización
     sin pedirlo explícitamente). Si se vuelve a correr el orquestador
     completo en una máquina local con carpeta `downloads/` vieja, el
     mismo problema se puede repetir. Posible fix futuro: que
     `sync_files.py` suba a Storage en vez de escribir la ruta local
     directamente (igual que hace `_upload_to_storage` en
     `sire_bot_orchestrator.py`), o que solo escanee el subdirectorio del
     RUC/periodo que se acaba de descargar.

## Hitos más importantes de la sesión 1

1. **Bug del botón "Autenticar y Descargar Físicos" (SUNAT)** — el scraper
   (`download_xml_scraper.py`) fallaba en el 100% de los comprobantes con
   `Could not select tipoComprobante: Timeout 5000ms exceeded`, en cascada
   con `no_descargable`. Se investigó la causa raíz (dropdown de SUNAT
   renderizando más lento de lo que el timeout esperaba) y se armó un fix,
   pero **por pedido explícito del usuario se revirtió** y se dejó el
   scraper tal como estaba originalmente — solo se re-habilitó el botón del
   frontend (commits `1d23924` → revertido → reaplicado en `01a2d98`).

2. **Bug de tarjetas/íconos "pendiente" en Compras y Ventas** — las
   descargas SÍ se guardaban bien en la base de datos (`estado_xml`/
   `estado_pdf = 'DESCARGADO'`), pero el frontend comparaba contra el string
   `'COMPLETADO'`, que el backend nunca escribe. Se corrigió para que
   reconozca los estados reales (`DESCARGADO`, `PENDIENTE`, `ERROR`,
   `NO_DESCARGABLE`/`NO_EXISTE`). Commit `558947d`.

3. **Botones de descarga XML/PDF por fila** — no tenían `onClick`. Se creó
   el endpoint `GET /api/bot/comprobante-file/{id}?tipo=xml|pdf` y se
   conectaron los botones en `ComprasView.jsx`/`VentasView.jsx`.
   Commit `2a02e75`.

4. **Hallazgo importante: los archivos descargados desaparecían en cada
   deploy de Railway** — el disco de Railway es efímero; la ruta guardada
   en `ruta_xml`/`ruta_pdf` era un path local que se borraba en cada push.
   El usuario aclaró que el sistema debía usar Supabase Storage (como el
   resto de la app), así que se migró todo el pipeline:
   - Nuevo bucket privado `comprobantes-fisicos` en Supabase Storage.
   - `sire_bot_orchestrator.py` ahora sube cada XML/PDF a Storage justo
     al descargarlo.
   - El endpoint de descarga ahora lee de Storage, no del disco.
   - `sync_files.py` ya no revierte a `PENDIENTE` por ausencia del disco
     local (Storage es la fuente de verdad).
   - Verificado end-to-end con una subida/descarga de prueba real contra
     producción (Railway). Commit `336d130`.

5. **Persistencia de pantalla ante reload** — la pestaña activa, el
   cliente y el periodo seleccionados se perdían al refrescar (F5), volviendo
   a una pantalla en blanco. Ahora se guardan en `localStorage` y se
   restauran automáticamente, con un fallback a "dashboard" si el rol del
   usuario ya no tiene permiso sobre la pestaña recordada. Commit `8aeb9a1`.

## Lo que falta por hacer / se intentó pero no se pudo

- **El bug original del scraper de SUNAT sigue sin resolver.** Hay 15
  comprobantes del proveedor RUC `20100047218` (cliente PROSPERY VIAJES,
  periodo 202607) marcados `NO_EXISTE` que fallan por el mismo timeout del
  dropdown `tipoComprobante`. El fix ya se diseñó y se probó una vez
  (commit `7cf7747`, revertido en `bfe2d50`) pero el usuario pidió dejar el
  scraper "tal como lo encontró". **Sigue pendiente decidir si se vuelve a
  aplicar ese fix.**
- ~~No se pudo verificar el pipeline de Storage con una descarga 100% real~~
  **RESUELTO en sesión 2 (2026-09-19, ver arriba):** se corrió el
  orquestador real (login + descarga + upload) contra SUNAT y Storage de
  producción, con verificación de contenido en el bucket y en el endpoint
  de descarga de Railway. El login vía Railway sigue fallando (ver
  diagnóstico de IP de datacenter arriba), pero el pipeline de Storage en
  sí ya está confirmado end-to-end.
- **Nuevo pendiente (sesión 2):** decidir si vale la pena endurecer
  `sync_files.py` para que suba a Storage en vez de escribir rutas locales
  (ver hallazgo #4 de la sesión 2) — hoy es seguro solo si corre en
  Railway inmediatamente después de una descarga.
- **Procesamiento** todavía tiene sus dos botones sin conectar: "Extraer
  Glosas de XML" y "Clasificar con Inteligencia Artificial" (probablemente
  `/api/bot/enrich-xml` y `/api/bot/classify-ai`, que ya existen en el
  backend pero no están wireados al frontend).
- **Facturación** (`/api/facturacion/emitir`, `/api/facturacion/estado`)
  tampoco está conectada a ningún botón todavía.
- El logo real (`logo quanta.png`) sigue sin reintegrarse a la app ni a la
  landing — el usuario pidió dejarlo en texto ("Q + Quanta") hasta que lo
  "formatee" bien más adelante.
- La landing page todavía tiene contenido de relleno (precios de ejemplo,
  testimonios genéricos, contacto falso) — el usuario dijo que eso se cierra
  después.

## Las últimas 3 cosas que hicimos (en orden)

1. **Persistencia de Storage para los físicos de SUNAT** (bucket +
   `sire_bot_orchestrator.py` + endpoint + `sync_files.py`) — commit
   `336d130`, desplegado y verificado con una prueba simulada real contra
   producción.
2. **Persistencia de pantalla ante reload** (pestaña, cliente y periodo en
   `localStorage`) — commit `8aeb9a1`, desplegado.
3. **Triage de un finding de `impeccable`** sobre el borde lateral de los
   toasts de notificación (`App.jsx` línea 834) — se confirmó que es el
   mismo falso positivo ya evaluado antes en la sesión (borde de severidad
   funcional, no decorativo) y se persistió como excepción sancionada vía
   `impeccable hooks ignore-value side-tab "*" --file src/App.jsx`.
