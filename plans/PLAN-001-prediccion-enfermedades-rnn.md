# Implementation Plan: PLAN-001 — Sistema de Predicción de Enfermedades con RNN

> **Status:** Under Review
> **Specification:** specs/SPEC-001-prediccion-enfermedades-rnn.md
> **Author:** Sistema SDD
> **Date:** 2026-05-24
> **Approved by:** _Pending_

---

## 1. Overview

**Approach:**
Sistema monolítico modular con 4 scripts independientes (`update_from_apis.py`, `import_csv.py`, `train_model.py`, `app.py`) que comparten una base SQLite común y modelos TensorFlow/Keras serializados. El frontend es HTML/CSS/JS estático servido por FastAPI con Plotly.js para gráficos interactivos. Datos sintéticos para demostración.

**Key Design Decisions:**
- **SQLite sobre PostgreSQL**: Elimina dependencia de servidor externo, portabilidad total, misma API Python.
- **Modelos separados por enfermedad**: 3 modelos LSTM independientes (hantavirus, COVID, dengue) en vez de multi-salida. Mayor simplicidad, tolerancia a fallos, y extensibilidad.
- **HTML estático + Plotly.js + Fetch API**: Sin framework JS pesado. Carga directa desde FastAPI con polling cada 60s.
- **Datos sintéticos generados con ruido controlado**: Bases de casos reales de SLP (clima, estacionalidad) para simular comportamientos verosímiles.

---

## 2. Architecture

### 2.1. Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        project_root/                                 │
│                                                                     │
│  ┌──────────────┐   ┌──────────────────┐   ┌─────────────────────┐  │
│  │ update_from  │   │  import_csv.py   │   │    app.py            │  │
│  │ _apis.py     │   │  (carga manual)  │   │  (FastAPI + static)  │  │
│  └──────┬───────┘   └────────┬─────────┘   └──────────┬──────────┘  │
│         │                    │                         │             │
│         └────────┬───────────┘                         │             │
│                  ▼                                     │             │
│  ┌──────────────────────────────┐                     │             │
│  │     src/database.py          │                     │             │
│  │     (SQLite conexión + CRUD) │                     │             │
│  └──────────────┬───────────────┘                     │             │
│                 │                                     │             │
│                 ▼                                     ▼             │
│  ┌──────────────────────────────┐   ┌─────────────────────────────┐ │
│  │     data/database.db         │   │  src/predictor.py            │ │
│  │   (SQLite — BD principal)    │   │  (cargar modelo + predecir) │ │
│  └──────────────────────────────┘   └──────────────┬──────────────┘ │
│                                                     │               │
│  ┌──────────────────────────────┐                   │               │
│  │  src/train_model.py          │───────────────────┘               │
│  │  (TensorFlow LSTM)           │                                   │
│  └──────────────┬───────────────┘                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────┐                                   │
│  │  models/*.keras              │                                   │
│  │  (modelos serializados)      │                                   │
│  └──────────────────────────────┘                                   │
│                                                                     │
│  ┌──────────────────────────────┐                                   │
│  │  static/                     │                                   │
│  │  ├── index.html              │                                   │
│  │  ├── css/style.css           │                                   │
│  │  └── js/ (dashboard, charts, │                                   │
│  │       map)                   │                                   │
│  └──────────────────────────────┘                                   │
│                                                                     │
│  ┌──────────────────────────────┐                                   │
│  │  presentacion/               │                                   │
│  │  └── presentacion.tex        │                                   │
│  └──────────────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2. Technology Choices

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Lenguaje | Python 3.10+ | Requisito del proyecto, ecosistema ML maduro |
| ML Framework | TensorFlow/Keras 2.x | Seleccionado por usuario, mejor para producción |
| Backend | FastAPI | Async, auto-docs, validación Pydantic, rápido |
| Base de Datos | SQLite | Portátil, sin servidor, misma API que PostgreSQL |
| Visualización | Plotly.js | Gráficos interactivos, mapas de calor, sin backend pesado |
| Trends | pytrends | Única librería Python madura para Google Trends |
| Google Sheets | gspread | Fase 2, opcional |
| Presentación | LaTeX Beamer | Plantillas existentes en el harness SDD |

---

## 3. File Structure

### New Files
| File Path | Purpose |
|-----------|---------|
| `requirements.txt` | Dependencias Python del proyecto |
| `.env.example` | Variables de entorno (template) |
| `data/processed/sample_import.csv` | CSV de ejemplo para importación manual |
| `src/__init__.py` | Package init |
| `src/database.py` | Conexión SQLite, creación de tablas, CRUD |
| `src/data_sources/__init__.py` | Package init |
| `src/data_sources/google_trends.py` | Wrapper pytrends para keywords por enfermedad |
| `src/data_sources/government_apis.py` | Wrapper APIs gobierno (con fallback controlado) |
| `src/synthetic_data.py` | Generador de datos sintéticos realistas |
| `src/import_csv.py` | Script CLI: validar e insertar CSV en BD |
| `src/update_from_apis.py` | Pipeline diario: Trends + APIs → BD |
| `src/train_model.py` | Script CLI: entrenar RNN por enfermedad |
| `src/predictor.py` | Cargar modelo, predecir, calcular métricas |
| `src/app.py` | Servidor FastAPI + rutas API + frontend estático |
| `static/index.html` | Dashboard principal con selectores de enfermedad |
| `static/css/style.css` | Estilos del dashboard |
| `static/js/dashboard.js` | Lógica principal: polling, eventos, estado |
| `static/js/charts.js` | Gráficos Plotly: series temporales |
| `static/js/map.js` | Mapa de calor de SLP por municipio |
| `scripts/seed_all.sh` | Script one-shot: generar datos sintéticos + entrenar modelos |
| `presentacion/presentacion.tex` | Presentación LaTeX Beamer del proyecto |
| `presentacion/presentacion.bib` | Bibliografía de la presentación |
| `tests/conftest.py` | Fixtures compartidos de pytest |
| `tests/test_database.py` | Tests de operaciones BD |
| `tests/test_import_csv.py` | Tests de importación CSV |
| `tests/test_predictor.py` | Tests de carga de modelo y predicción |
| `tests/test_api.py` | Tests de endpoints FastAPI |

### Modified Files
None (new project).

### Deleted Files
None.

---

## 4. Dependencies

| Dependency | Version | Purpose | New? |
|-----------|---------|---------|------|
| tensorflow | >=2.10 | RNN LSTM/GRU | Yes |
| fastapi | >=0.100 | Backend web | Yes |
| uvicorn | >=0.20 | Servidor ASGI | Yes |
| pandas | >=2.0 | Manipulación de datos | Yes |
| numpy | >=1.24 | Cómputo numérico | Yes |
| pytrends | >=4.9 | Google Trends API | Yes |
| pydantic | >=2.0 | Validación de datos | Yes |
| plotly | >=5.15 | Gráficos (python, para generar JSON) | Yes |
| scikit-learn | >=1.3 | Métricas de evaluación | Yes |
| gspread | >=6.0 | Google Sheets (opcional, fase 2) | No |
| pytest | >=7.0 | Testing | Yes |
| python-dotenv | >=1.0 | Variables de entorno | Yes |
| aiofiles | >=23.0 | Archivos async (subida CSV por web) | Yes |

---

## 5. Task Breakdown

### Task 1: Project Scaffolding y Configuración
- **ID:** TASK-01
- **_Boundary_:** `requirements.txt`, `.env.example`, `src/__init__.py`, `scripts/`, `data/`
- **_Depends_:** None
- **Description:** Crear estructura de directorios, requirements.txt con todas las dependencias, archivo .env.example, y scripts/seed_all.sh.
- **Tests:** Verificar que `pip install -r requirements.txt` se completa sin errores.
- **Estimated complexity:** Low

### Task 2: Base de Datos — Esquema y CRUD
- **ID:** TASK-02
- **_Boundary_:** `src/database.py`
- **_Depends_:** TASK-01
- **Description:** Implementar `database.py` con:
  - Conexión SQLite (archivo `data/database.db`)
  - Creación automática de tablas: `search_trends`, `epidemiological_data`, `clinical_data`, `disease_municipality_risk`
  - Funciones CRUD: insert_trends, insert_epidemiological, get_timeseries, get_municipality_data, get_latest_data
  - Esquema completo con campos (fecha, enfermedad, municipio, casos, hospitalizaciones, muertes, keyword, valor_trend)
- **Tests:** pytest para crear BD, insertar registros, consultar series temporales.
- **Estimated complexity:** Medium

### Task 3: Generador de Datos Sintéticos
- **ID:** TASK-03
- **_Boundary_:** `src/synthetic_data.py`, `data/synthetic_data/`
- **_Depends_:** TASK-02
- **Description:** Implementar generador de datos sintéticos que simule:
  - 2 años de datos diarios (2024-01 a 2026-05)
  - Patrones estacionales (dengue en lluvias, COVID en invierno)
  - Ruido controlado y correlación entre trends y casos
  - Todos los 58 municipios de SLP con diferentes niveles de población
  - Keywords de Google Trends para las 3 enfermedades
- **Tests:** Verificar que los datos generados tienen el formato correcto, sin valores nulos, rangos válidos.
- **Estimated complexity:** Medium

### Task 4: Pipeline de Datos — Google Trends
- **ID:** TASK-04
- **_Boundary_:** `src/data_sources/google_trends.py`, `src/data_sources/government_apis.py`
- **_Depends_:** TASK-02
- **Description:** Implementar:
  - `google_trends.py`: Wrapper pytrends con ExactTrend, batch de keywords por enfermedad, manejo de rate limits, fallback graceful
  - `government_apis.py`: Wrapper para APIs gubernamentales con manejo de errores (simulado para fase 1)
- **Tests:** Mock de pytrends para verificar parseo de resultados y almacenamiento en BD.
- **Estimated complexity:** Low

### Task 5: Importación Manual de CSV
- **ID:** TASK-05
- **_Boundary_:** `src/import_csv.py`, `data/processed/sample_import.csv`
- **_Depends_:** TASK-02
- **Description:** Implementar `import_csv.py` (script CLI) que:
  - Lee CSV con columnas: fecha, municipio, enfermedad, casos, hospitalizaciones, muertes
  - Valida formato y tipos de datos
  - Inserta en BD con logging detallado
  - Reporta resumen de registros insertados/errores
  - Genera archivo CSV de ejemplo
- **Tests:** pytest con CSVs válidos, inválidos, parcialmente válidos.
- **Estimated complexity:** Low

### Task 6: Pipeline Diario Combinado
- **ID:** TASK-06
- **_Boundary_:** `src/update_from_apis.py`
- **_Depends_:** TASK-04, TASK-05
- **Description:** Implementar `update_from_apis.py` que:
  - Ejecuta extracción de Google Trends
  - Intenta APIs gubernamentales (captura excepciones sin detener pipeline)
  - Registra éxito/fallo de cada fuente en log
  - Si es domingo, dispara reentrenamiento automático
- **Tests:** Verificar que el script corre sin excepciones incluso con APIs caídas.
- **Estimated complexity:** Low

### Task 7: Modelo RNN — Arquitectura y Entrenamiento
- **ID:** TASK-07
- **_Boundary_:** `src/train_model.py`, `src/predictor.py`, `models/`
- **_Depends_:** TASK-03, TASK-06
- **Description:** Implementar:
  - `train_model.py`: Arquitectura LSTM bidireccional (2 capas, 64-128 unidades, Dropout 0.3, Dense con sigmoid + ReLU), preparación de secuencias de 21 días, entrenamiento con early stopping, validación temporal, guardado a `models/{enfermedad}_model.keras`
  - `predictor.py`: Carga de modelo, predicción a 7 días, cálculo de métricas (sensibilidad, especificidad, RMSE), guardado histórico de predicciones
- **Tests:** Verificar shape de input/output, que el modelo converge, que las predicciones están en rangos válidos.
- **Estimated complexity:** High

### Task 8: Semilla de Datos + Entrenamiento Inicial
- **ID:** TASK-08
- **_Boundary_:** `scripts/seed_all.sh`
- **_Depends_:** TASK-03, TASK-07
- **Description:** Script `seed_all.sh` que:
  - Ejecuta generación de datos sintéticos → BD
  - Ejecuta entrenamiento de modelos (3 enfermedades)
  - Verifica que las predicciones se generan correctamente
- **Tests:** Ejecución completa del script verifica pipeline de extremo a extremo.
- **Estimated complexity:** Low

### Task 9: Backend FastAPI — Endpoints REST
- **ID:** TASK-09
- **_Boundary_:** `src/app.py`
- **_Depends_:** TASK-02, TASK-07
- **Description:** Implementar FastAPI con endpoints:
  - `GET /` → Sirve `static/index.html`
  - `GET /api/dashboard/{enfermedad}` → JSON con datos completos del dashboard
  - `GET /api/timeseries/{enfermedad}` → Series temporales (reales + predichas)
  - `GET /api/heatmap/{enfermedad}` → Datos geo para mapa de calor por municipio
  - `GET /api/metrics/{enfermedad}` → Métricas del modelo
  - `POST /api/upload-csv` → Subir CSV (multipart)
  - `POST /api/retrain/{enfermedad}` → Disparar reentrenamiento
  - Scheduler interno cada 60s para verificar nuevos datos (simplified)
- **Tests:** pytest con TestClient de FastAPI, verificar endpoints.
- **Estimated complexity:** High

### Task 10: Frontend Web — Dashboard con Plotly.js
- **ID:** TASK-10
- **_Boundary_:** `static/index.html`, `static/css/style.css`, `static/js/dashboard.js`, `static/js/charts.js`, `static/js/map.js`
- **_Depends_:** TASK-09
- **Description:** Implementar dashboard web responsive:
  - `index.html`: Selector de enfermedad (tabs), selector de período, área de gráficos
  - `style.css`: Tema oscuro/claro para datos de salud, diseño responsive
  - `dashboard.js`: Fetch API con polling cada 60s, manejo de estado, eventos
  - `charts.js`: Plotly.js con series temporales (casos reales, predichos, bandas de confianza)
  - `map.js`: Mapa de calor SLP con Plotly (choropleth), colores por nivel de riesgo
- **Tests:** Verificar carga visual en navegador, tiempos de carga < 3s.
- **Estimated complexity:** Medium

### Task 11: Presentación LaTeX Beamer
- **ID:** TASK-11
- **_Boundary_:** `presentacion/presentacion.tex`, `presentacion/presentacion.bib`
- **_Depends_:** TASK-08
- **Description:** Crear presentación académica LaTeX Beamer con:
  - Portada: título, autor, institución, fecha
  - Secciones: Introducción, Objetivos, Metodología, Arquitectura, Resultados, Conclusiones
  - Integrar gráficos generados por el sistema
  - Compilar con `pdflatex` y `bibtex`
- **Tests:** Verificar compilación sin errores con `pdflatex`.
- **Estimated complexity:** Low

### Task 12: Calidad — Tests y Gates
- **ID:** TASK-12
- **_Boundary_:** `tests/`, `rules/quality-gates.json`
- **_Depends_:** TASK-02, TASK-05, TASK-07, TASK-09
- **Description:** Escribir tests unitarios y de integración para todos los módulos:
  - `test_database.py`: CRUD, consultas, integridad
  - `test_import_csv.py`: Formatos válidos, inválidos, parciales
  - `test_predictor.py`: Carga de modelo, formato de output, sanity checks
  - `test_api.py`: Endpoints, status codes, payloads
  - Ejecutar `ruff`, `pytest`, verificar cobertura
- **Tests:** Los tests mismos son el entregable.
- **Estimated complexity:** Medium

---

## 6. Data Models

### Entity: search_trends
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER PK | Auto |
| date | DATE | Fecha del dato |
| keyword | VARCHAR(100) | Palabra clave buscada |
| value | FLOAT | Volumen de búsqueda (0-100) |
| region | VARCHAR(10) | MX o SLP |
| disease | VARCHAR(50) | Enfermedad asociada |
| created_at | TIMESTAMP | Fecha de inserción |

### Entity: epidemiological_data
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER PK | Auto |
| date | DATE | Fecha del registro |
| disease | VARCHAR(50) | Enfermedad |
| municipality | VARCHAR(100) | Municipio de SLP |
| confirmed_cases | INTEGER | Casos confirmados |
| hospitalizations | INTEGER | Hospitalizaciones |
| deaths | INTEGER | Muertes |
| source | VARCHAR(50) | Fuente (api, csv, sintetico) |
| created_at | TIMESTAMP | Fecha de inserción |

### Entity: clinical_data
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER PK | Auto |
| date | DATE | Fecha del registro |
| disease | VARCHAR(50) | Enfermedad |
| municipality | VARCHAR(100) | Ubicación |
| hantavirus_type | VARCHAR(50) | Tipo de hantavirus (si aplica) |
| dengue_severity | VARCHAR(20) | Grave/No grave (si aplica) |
| symptoms | TEXT | Síntomas reportados |
| source | VARCHAR(50) | google_forms, doctor, etc. |
| created_at | TIMESTAMP | Fecha de inserción |

### Entity: predictions
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER PK | Auto |
| date | DATE | Fecha de la predicción |
| disease | VARCHAR(50) | Enfermedad |
| municipality | VARCHAR(100) | Municipio |
| outbreak_probability | FLOAT | Probabilidad de brote (0-1) |
| estimated_cases_7d | FLOAT | Casos estimados próximos 7 días |
| ci_lower | FLOAT | Intervalo de confianza inferior |
| ci_upper | FLOAT | Intervalo de confianza superior |
| model_version | VARCHAR(20) | Versión del modelo |
| created_at | TIMESTAMP | Fecha de generación |

### Entity: model_metrics
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER PK | Auto |
| disease | VARCHAR(50) | Enfermedad |
| sensitivity | FLOAT | Sensibilidad (>75%) |
| specificity | FLOAT | Especificidad |
| rmse | FLOAT | Root Mean Square Error |
| precision | FLOAT | Precisión |
| accuracy | FLOAT | Exactitud |
| trained_at | TIMESTAMP | Fecha de entrenamiento |
| training_duration_s | FLOAT | Duración del entrenamiento |
| num_epochs | INTEGER | Épocas ejecutadas |

---

## 7. Error Handling Strategy

| Error Scenario | Handling Strategy | User Impact |
|---------------|-------------------|-------------|
| API gobierno caída | Capturar excepción, loguear warning, continuar pipeline | Sin impacto (usa Trends + datos existentes) |
| pytrends sin internet | Capturar timeout/connection error, loguear, no detener pipeline | Datos de Trends no actualizados |
| CSV inválido (formato) | Validar cada fila, reportar errores específicos, no insertar nada | Mensaje de error detallado al admin |
| CSV con datos parciales | Insertar filas válidas, reportar filas erróneas | Inserción parcial con advertencia |
| Modelo no entrenado | Retornar mensaje "Modelo no disponible" en API | Dashboard muestra sección sin datos |
| Training falla (divergencia) | Capturar NaN loss, early stopping, mantener modelo anterior | Modelo anterior sigue activo |
| BD bloqueada (concurrencia) | Usar WAL mode en SQLite, timeout 5s | Operación reintenta automáticamente |
| Archivos estáticos no encontrados | FastAPI retorna 404 con página básica | Navegador muestra error 404 |

---

## 8. Implementation Notes

*Esta sección se llena DURANTE `/implement`. Do not delete existing notes.*

---

## 9. Verification Plan

### Automated Tests
- [ ] `ruff check src/ tests/` — Sin errores de linting
- [ ] `pytest tests/ -v` — Todos los tests pasan
- [ ] `python src/import_csv.py data/processed/sample_import.csv` — Importación exitosa
- [ ] `python src/train_model.py --disease hantavirus` — Entrenamiento converge

### Manual Verification
- [ ] Iniciar servidor: `uvicorn src.app:app --reload`
- [ ] Abrir `http://localhost:8000` — Dashboard carga en < 3s
- [ ] Seleccionar cada enfermedad — Gráficos se actualizan
- [ ] Subir CSV via web — Datos reflejados inmediatamente
- [ ] Ejecutar `python src/import_csv.py nuevo.csv` — Datos en BD y dashboard
- [ ] Compilar presentación LaTeX sin errores
- [ ] Verificar mapa de calor con 58 municipios de SLP

---

## 10. Rollback Plan

- **Paso 1:** `git checkout HEAD~1` para revertir último cambio
- **Paso 2:** `rm data/database.db && python src/database.py` para recrear BD limpia
- **Paso 3:** `python src/seed_all.sh` para regenerar datos sintéticos + modelos
- **Paso 4:** Si un modelo .keras está corrupto, eliminar archivo y reentrenar
