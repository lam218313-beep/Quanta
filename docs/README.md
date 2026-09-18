# Sistema Bot de Contabilidad - Descarga y Enriquecimiento (SIRE + XML)

Este sistema automatiza la descarga de comprobantes electrónicos desde la plataforma SIRE de SUNAT (API) y la descarga física de los XMLs mediante un bot de Playwright. Soporta múltiples empresas (Multi-tenant).

## 🏢 1. Cómo Registrar una Nueva Empresa

Para que el bot procese los datos de una nueva empresa, debes hacer dos cosas: registrar sus credenciales en la base de datos y generar sus cookies de sesión para el bot.

### Paso 1: Registrar Credenciales en la Base de Datos
1. Ve a **Supabase Studio** abriendo `http://127.0.0.1:54323` en tu navegador.
2. En el menú izquierdo, haz clic en **Table Editor** y selecciona la tabla `clientes`.
3. Haz clic en **Insert row** y llena los siguientes campos con la información de la empresa:
   - `ruc`: El RUC de la empresa (11 dígitos).
   - `razon_social`: El nombre de la empresa.
   - `usuario_sol`: El **Usuario SOL** (Ojo: solo el usuario, no incluyas el RUC aquí).
   - `clave_sol`: La contraseña del usuario SOL.
   - `client_id_api`: El Client ID generado en el portal de SUNAT (Credenciales de API).
   - `client_secret_api`: El Client Secret generado en el portal.
4. *(La columna `id` déjala vacía, se generará sola)*. Haz clic en **Save**.

### Paso 2: Generar las Cookies de Navegación (Para el Bot)
El bot que descarga los XMLs necesita permisos para entrar al portal antiguo de SUNAT. Ejecuta este comando en tu terminal reemplazando `<RUC>` por el RUC de la empresa:

```bash
python app/brain/automation_scraper.py --ruc <RUC>
```
Se abrirá un navegador de Chrome. **Inicia sesión manualmente**. Una vez adentro, ve a:
`Empresas -> Comprobantes de Pago -> Consulta de Comprobantes de Pago -> Nueva Consulta de comprobantes de pago`
Y espera unos segundos hasta que la consola diga **Success!**. Esto creará un archivo `sunat_session_<RUC>.json` que el bot usará más adelante.

---

## 🚀 2. Ciclo de Trabajo (Comandos Diarios/Mensuales)

Una vez que tengas tus empresas registradas, el flujo de trabajo para obtener toda la información contable consta de 3 comandos que debes ejecutar en orden:

### Comando 1: Obtener Propuestas del SIRE (Ventas y Compras)
Este comando se conecta vía API a SUNAT para todas las empresas activas en la base de datos y descarga los libros preliminares (TXT). Automáticamente carga esta información básica en la base de datos.
```bash
python app/brain/sire_download_cli.py --period 202501
```
*(Si falla por conexión o quieres volver a intentar solo lo que falta sin duplicar, agrégale `--skip-sire` al final).*

### Comando 2: Bot Orquestador de Descarga de XMLs
Este comando toma todos los registros pendientes en la base de datos y abre Chrome silenciosamente para descargar los archivos `.xml` originales y los PDFs. Automáticamente cambiará de cuenta según la empresa.
```bash
python app/brain/db/sire_bot_orchestrator.py --limit 200
```
*(Puedes ajustar el `--limit` según cuántos comprobantes quieras descargar de golpe).*

### Comando 3: Enriquecedor de Datos
Finalmente, este comando agarra todos los archivos `.xml` (o `.zip`) que descargó el bot, los lee, extrae todos los productos, cantidades e impuestos, y actualiza la base de datos para que tu Panel de Supabase esté al 100%.
```bash
python app/brain/db/sire_xml_enricher.py
```

---

## 💡 Trucos Útiles

- **Ver solo un cliente específico en el SIRE:** Si solo quieres procesar una empresa y no todas, usa:
  `python app/brain/sire_download_cli.py --period 202501 --client 20611775661`

- **Resetear comprobantes fallidos:** Si el Bot Orquestador marca archivos como "NO_EXISTE" o "ERROR" por fallos de red de la SUNAT, puedes resetearlos desde la consola SQL de Supabase para que vuelva a intentarlo:
  `UPDATE sire_comprobantes_fisicos SET estado_xml = 'PENDIENTE', reintentos = 0 WHERE tipo_libro = 'VENTAS';`

---

## 🖥️ 4. Ejecutar el Dashboard (Interfaz Gráfica)

Hemos añadido una hermosa interfaz gráfica para que controles los bots y veas los resultados sin tocar la consola. Para levantar todo:

1. **Asegúrate de que la Base de Datos esté corriendo (Docker):**
   ```bash
   npx supabase start
   ```

2. **Levantar la API de los bots (Backend):**
   Abre una nueva terminal en la raíz del proyecto y ejecuta:
   ```bash
   $env:PYTHONIOENCODING="utf-8"; python -m uvicorn app.api:app --reload --port 8000
   ```

3. **Levantar la Interfaz Gráfica (Frontend React/Vite):**
   Abre OTRA terminal, muévete a la carpeta frontend y ejecuta:
   ```bash
   cd frontend
   npm run dev
   ```

Finalmente, abre en tu navegador: [http://localhost:5173/](http://localhost:5173/)
