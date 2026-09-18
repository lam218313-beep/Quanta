# 🏗️ Arquitectura General del Sistema SIRE - Quanta

Este documento detalla la arquitectura de software, el stack tecnológico y los flujos de proceso para la automatización de descargas del Sistema Integrado de Registro Electrónico (SIRE) de la SUNAT, operando bajo un modelo multicliente secuencial y en entorno local.

---

## 1. 🔄 Lógica General del Cambio (De Script a Sistema Multicliente)

El sistema evoluciona de un script de ejecución lineal (basado en un archivo CSV de configuración) a una **arquitectura basada en estados y colas respaldadas por base de datos (Database-backed Queue)**. 

### ¿Por qué este cambio?
* **Escalabilidad Multicliente:** Permite gestionar 30 o más clientes de forma ordenada, sabiendo exactamente en qué paso se quedó cada uno.
* **Seguridad y Estabilidad (Ejecución Secuencial):** Al procesar un cliente a la vez ("uno a la vez"), se evita la saturación de memoria RAM (crítico al usar navegadores invisibles) y se previenen bloqueos temporales de IP por parte de la SUNAT (IP Ban).
* **Resiliencia ante fallos:** Si la SUNAT se cae o la computadora se reinicia, el sistema no empieza desde cero; lee la base de datos y retoma la descarga de la factura exacta que faltaba.

---

## 2. 💻 Stack Tecnológico

La arquitectura se sustenta en herramientas modernas diseñadas para convivir en el entorno local del estudio contable:

* **Lenguaje Principal:** Python 3.x
* **Framework Backend / API:** FastAPI + Uvicorn (Para exponer endpoints locales y orquestar el cerebro del sistema).
* **Base de Datos y Máquina de Estados:** **Supabase Local (PostgreSQL)**. Reemplaza al CSV y a herramientas externas de colas (como Redis/Celery). PostgreSQL maneja la concurrencia y los estados de cada cliente.
* **Automatización Web (RPA):** Playwright. Utilizado exclusivamente para la navegación "headless" (invisible) en el portal SOL y la descarga de archivos físicos (XML/PDF).
* **Consumo de API:** Librerías `requests` y `httpx` para interactuar con los endpoints oficiales OAuth2 del SIRE (SUNAT).
* **Procesamiento de Archivos:** Librería estándar `zipfile` y manipulación de cadenas en memoria para parsear los archivos `.txt` nativos.

---

## 3. ⚙️ Procesos Previos y Flujo de Trabajo (End-to-End)

El ciclo de vida del procesamiento de un periodo contable se divide en las siguientes etapas lógicas, ejecutadas de forma secuencial por el Worker de Python:

### Fase A: Preparación y Orquestación
1. **Lectura de Repositorio:** El sistema lee la tabla de `clientes` en Supabase para obtener las credenciales (RUC, Usuario SOL, Claves y API Keys) de las empresas activas.
2. **Definición de Trabajo:** Se determina el periodo tributario a procesar (Ej. `202401`) y el bot comienza a iterar cliente por cliente.

### Fase B: Extracción de la Propuesta Oficial (Vía API SIRE)
*Esta fase se ejecuta 100% mediante peticiones HTTP, sin abrir navegadores.*
1. **Autenticación API:** Se genera el token OAuth2 usando `client_id` y `client_secret` proporcionados por SUNAT.
2. **Solicitud de Ticket:** Se solicita a SUNAT el reporte de la propuesta del RCE (Compras) y RVIE (Ventas).
3. **Polling y Descarga:** El sistema consulta periódicamente el estado del ticket. Al estar "Terminado", descarga el ZIP y extrae el archivo `.txt` nativo en memoria.
4. **Vaciado de Datos (Espejo):** El contenido del `.txt` se inserta directamente y sin alteraciones en las tablas `sire_preliminar_compras` y `sire_preliminar_ventas`.

### Fase C: Validación y Descarga Física (Vía Playwright)
*Esta fase utiliza el navegador invisible para obtener los sustentos físicos.*
1. **Autenticación SOL:** Playwright abre el portal web de SUNAT, se loguea y guarda las cookies de sesión (`sunat_session.json`).
2. **Cruce de Información:** El script consulta la base de datos para comparar las tablas preliminares contra la tabla de comprobantes físicos. Determina qué archivos XML y PDF aún no han sido descargados.
3. **Scraping Secuencial:** Navega a la sección de "Mis Comprobantes", busca específicamente las series y números faltantes, y descarga los archivos a la carpeta local correspondiente (`/descargas/[RUC]/[PERIODO]/`).
4. **Actualización de Estado:** Marca en la base de datos que el XML/PDF de esa fila específica ha sido descargado exitosamente.

### Fase D: Post-Procesamiento (Próximos pasos)
1. Extracción de detalles internos de los XML (como la `descripcion_comprobante`).
2. Generación de los archivos Excel tabulados si se requiere revisión manual.
3. Envío de datos consolidados hacia el ERP (Odoo).

---

## 4. 🗄️ Arquitectura de Datos (Módulo Preliminar)

Tal como se definió en las fases de análisis, la base de datos separa conceptualmente la información para evitar columnas vacías y respetar al 100% las estructuras de SUNAT.

* **`clientes`:** Repositorio maestro de credenciales (Sin lógica transaccional).
* **`sire_preliminar_compras`:** Espejo 1:1 del archivo TXT de Propuesta RCE de SUNAT. Contiene la información unificada de todos los clientes y periodos, filtrable por `cliente_id` e índices compuestos.
* **`sire_preliminar_ventas`:** Espejo 1:1 del archivo TXT de Propuesta RVIE de SUNAT.
* *(Tablas de cruce de comprobantes físicos y control de colas por definir en la siguiente iteración).*

