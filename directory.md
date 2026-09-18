# Directorio del Proyecto Contax Brain

Este documento detalla la estructura principal del proyecto, explicando la utilidad y funcionalidades más importantes de cada archivo y directorio. El proyecto es un sistema de automatización contable impulsado por IA, diseñado específicamente para Perú (integración con SUNAT y Odoo).

## 📁 Raíz del Proyecto

*   **`app/`**: Directorio principal del backend (Python/FastAPI). Contiene toda la lógica de negocio, automatización de descargas (SUNAT), procesamiento de datos y la API.
*   **`frontend/`**: Directorio principal del frontend (React + Vite). Contiene la interfaz de usuario.
*   **`supabase/`**: Configuraciones locales, migraciones y datos semilla para la base de datos Supabase.
*   **`docs/`**: Documentación técnica del proyecto.
*   **`downloads/`**: Carpeta temporal para las descargas de archivos (XML, PDF, TXT) obtenidos de SUNAT.
*   **`all_migrations.sql`**: Script SQL consolidado que contiene todas las migraciones, tablas, vistas y políticas RLS de la base de datos Supabase.
*   **`patch_api.py`**: Script de utilidad en la raíz, probablemente utilizado para aplicar parches o tareas administrativas sobre la API o la base de datos.
*   **`Dockerfile`**: Definición para contenedorizar la aplicación (probablemente el backend).
*   **`requirements.txt`**: Lista de dependencias de Python para el backend.
*   **`.env`**: Archivo de variables de entorno (credenciales, URLs de Supabase, Odoo).

---

## 💻 Backend (`app/`)

### Archivos Principales
*   **`api.py`**: Archivo extenso que levanta servicios adicionales de FastAPI, manejando tareas en segundo plano (BackgroundTasks) para la ejecución asíncrona de los bots (scrapers de SUNAT) vía subprocesos, gestionando sus logs y estados.
*   **`cli_export.py`**, **`sire_download_cli.py`**, **`sire_txt_to_excel.py`**, **`sire_xml_scrape_cli.py`**: Scripts de interfaz de línea de comandos (CLI) que sirven como puntos de entrada para ejecutar tareas específicas (descarga de comprobantes, conversión de TXT del SIRE a Excel, scraping de XMLs).

### 🧠 Core Lógico (`app/brain/`)
Es el corazón del sistema, organiza las rutas de la API y los scripts de automatización.
*   **`main.py`**: Punto de entrada de la API REST principal construida con FastAPI. Registra las rutas (`documents`, `linking`, `analytics`) y provee endpoints de *health check* para verificar conexión con Supabase y Odoo.
*   **`automation_scraper.py`**: Script con Playwright para realizar el flujo de autenticación (login) automático o manual en el portal SUNAT SOL y guardar las cookies de sesión (ej. `sunat_session_*.json`).
*   **`download_xml_scraper.py`**: Scraper asíncrono avanzado con Playwright que navega por el portal SUNAT (Consulta de Comprobantes de Pago) para descargar masivamente los XML/PDF de compras y ventas.
*   **`config.py`**: Manejo de configuraciones del entorno para el módulo brain.

#### 🗄️ Base de Datos y Orquestación (`app/brain/db/`)
*   **`supabase_client.py`**: Cliente Singleton para conectarse a Supabase.
*   **`odoo_client.py`**: Cliente XML-RPC para la integración bidireccional con el ERP Odoo (sincronización de facturas, partners).
*   **`sire_bot_orchestrator.py`**: Orquestador fundamental que consulta a la base de datos (Supabase) por comprobantes físicos pendientes y coordina las colas de descarga utilizando los scrapers de Playwright. Maneja los reintentos y estados.
*   **`ai_classifier.py`**: Módulo que probablemente utiliza IA (LLMs) para analizar, extraer información y sugerir la clasificación contable de los comprobantes.
*   **`sire_db_inserter.py`**, **`sire_txt_exporter.py`**, **`excel_exporter.py`**: Scripts encargados de la transformación y carga (ETL) de los datos en la base de datos y su exportación a formatos manejables para el contador.

#### 🌐 Endpoints (`app/brain/routes/`)
*   **`documents.py`**: Endpoints para la gestión y carga de documentos comprobantes.
*   **`sire.py`**: Endpoints específicos para la integración y procesamiento del SIRE (Sistema Integrado de Registros Electrónicos).
*   **`analytics.py`**: Endpoints para reportes y dashboards.
*   **`linking.py`**: Endpoints para la vinculación/conciliación de comprobantes.

#### 🛡️ Validación (`app/brain/validation/`)
*   **`validators.py`**: Reglas de negocio y de formato para validar que los RUCs, montos y estructuras de comprobantes sean correctos antes de insertarlos en BD o enviarlos a Odoo.

---

## 🎨 Frontend (`frontend/`)

Aplicación React empaquetada con Vite que proporciona el dashboard del sistema.

### Directorios y Archivos Principales
*   **`src/App.jsx`**: El componente raíz de la aplicación React. Define el enrutamiento (React Router), el layout general, barras de navegación y los proveedores de contexto global.
*   **`src/index.css`** y **`src/App.css`**: Hojas de estilo globales.
*   **`src/supabaseClient.js`**: Cliente instanciado de SupabaseJS para las operaciones directamente desde el frontend.
*   **`src/components/`**: Carpeta de componentes reutilizables.
    *   **`FacturacionView.jsx`**: Una de las vistas/componentes más importantes. Interactúa con el backend y Supabase para mostrar el estado de la facturación, manejar las descargas del SIRE y controlar los bots.
    *   **`Facturacion.css`**: Estilos específicos para la vista de facturación.
*   **`package.json`** / **`vite.config.js`**: Dependencias de Node (React, tailwind o librerías de UI) y configuración del bundler Vite.

---

## 🗄️ Base de Datos (`supabase/`)

*   **`migrations/`**: Directorio donde se guardan los archivos `.sql` incrementales que definen la evolución del esquema de la BD.
*   **`seed.sql`**: Datos iniciales para pruebas (clientes de prueba, configuraciones por defecto).
*   **`config.toml`**: Configuración del entorno local de Supabase (puertos, settings de Postgres).
