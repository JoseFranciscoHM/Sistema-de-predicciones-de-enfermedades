# Task Breakdown: Sistema de Predicción de Enfermedades con RNN

> **Plan Reference:** plans/PLAN-001-prediccion-enfermedades-rnn.md
> **Date:** 2026-05-24
> **Total Tasks:** 12

---

## Status Legend

- `[ ]` — Not started
- `[/]` — In progress
- `[x]` — Completed
- `[!]` — Blocked (see notes)

---

## Priority Order

### Phase A: Foundation / Setup

- `[ ]` **TASK-01:** Project Scaffolding y Configuración
  - **_Boundary_:** `requirements.txt`, `.env.example`, `src/__init__.py`, `scripts/`, `data/`
  - **_Depends_:** None
  - **Description:** Crear estructura de directorios completa, archivo requirements.txt con todas las dependencias, .env.example, scripts/seed_all.sh. Inicializar repositorio git.
  - **Acceptance Criteria:**
    - [ ] `pip install -r requirements.txt` se completa sin errores
    - [ ] Todos los directorios existen: src/, data/, static/, models/, tests/, presentacion/, scripts/
  - **Tests:**
    - [ ] Verificación manual de `pip install`
  - **Complexity:** Low

- `[ ]` **TASK-02:** Base de Datos — Esquema y CRUD
  - **_Boundary_:** `src/database.py`
  - **_Depends_:** TASK-01
  - **Description:** Implementar database.py con SQLite. Crear tablas: search_trends, epidemiological_data, clinical_data, predictions, model_metrics. Funciones CRUD completas.
  - **Acceptance Criteria:**
    - [ ] Las 5 tablas se crean automáticamente al importar database.py
    - [ ] Insertar y consultar registros funciona correctamente
    - [ ] Consultas de serie temporal retornan formato esperado
  - **Tests:**
    - [ ] `tests/test_database.py`: test_create_tables, test_insert_trend, test_insert_epidemiological, test_get_timeseries, test_get_municipality_data
  - **Complexity:** Medium

- `[ ]` **TASK-03:** Generador de Datos Sintéticos
  - **_Boundary_:** `src/synthetic_data.py`, `data/synthetic_data/`
  - **_Depends_:** TASK-02
  - **Description:** Generador de datos sintéticos realistas con 2 años de datos diarios, patrones estacionales, 58 municipios, 3 enfermedades, correlación trends-casos.
  - **Acceptance Criteria:**
    - [ ] Genera datos para los 58 municipios de SLP
    - [ ] Datos tienen estacionalidad visible (dengue en lluvias, COVID en invierno)
    - [ ] Sin valores nulos ni rangos inválidos
    - [ ] Exporta a CSV y a BD
  - **Tests:**
    - [ ] `tests/test_synthetic_data.py`: test_shape, test_no_nulls, test_seasonal_patterns, test_municipalities_count
  - **Complexity:** Medium

### Phase B: Data Pipeline

- `[ ]` **TASK-04:** Pipeline de Datos — Google Trends + APIs
  - **_Boundary_:** `src/data_sources/google_trends.py`, `src/data_sources/government_apis.py`
  - **_Depends_:** TASK-02
  - **Description:** Wrapper pytrends con ExactTrend para keywords por enfermedad. Wrapper APIs gobierno con manejo de fallos. Batch processing y rate limiting.
  - **Acceptance Criteria:**
    - [ ] pytrends se conecta y extrae datos para todas las keywords
    - [ ] APIs gobierno fallan gracefulmente (sin crash) cuando no hay conexión
    - [ ] Datos se almacenan en BD correctamente
  - **Tests:**
    - [ ] Mock pytrends: verificar parseo de resultados
    - [ ] Mock requests: verificar fallback graceful
  - **Complexity:** Low

- `[ ]` **TASK-05:** Importación Manual de CSV
  - **_Boundary_:** `src/import_csv.py`, `data/processed/sample_import.csv`
  - **_Depends_:** TASK-02
  - **Description:** Script CLI `import_csv.py` que lee CSV, valida formato, inserta en BD. Genera archivo CSV de ejemplo. Reporta estadísticas de importación.
  - **Acceptance Criteria:**
    - [ ] CSV válido → todos los registros insertados
    - [ ] CSV inválido → error descriptivo, 0 registros insertados
    - [ ] CSV parcial → registros válidos insertados, inválidos reportados
    - [ ] CSV de ejemplo generado en data/processed/
  - **Tests:**
    - [ ] `tests/test_import_csv.py`: test_valid_csv, test_invalid_csv, test_partial_csv, test_sample_csv_generated
  - **Complexity:** Low

- `[ ]` **TASK-06:** Pipeline Diario Combinado
  - **_Boundary_:** `src/update_from_apis.py`
  - **_Depends_:** TASK-04, TASK-05
  - **Description:** Script que ejecuta Trends + APIs, registra resultados, y opcionalmente dispara reentrenamiento (domingo o flag manual).
  - **Acceptance Criteria:**
    - [ ] Ejecuta sin excepciones incluso con todas las APIs caídas
    - [ ] Log detallado de cada fuente (éxito/fallo)
    - [ ] Dispara reentrenamiento si es domingo
  - **Tests:**
    - [ ] Simular APIs caídas → verificar log y continuación
  - **Complexity:** Low

### Phase C: RNN Model

- `[ ]` **TASK-07:** Modelo RNN — Arquitectura y Entrenamiento
  - **_Boundary_:** `src/train_model.py`, `src/predictor.py`, `models/`
  - **_Depends_:** TASK-03, TASK-06
  - **Description:** Arquitectura LSTM bidireccional (2 capas, 64-128 unidades, Dropout 0.3), preparación de secuencias de 21 días, entrenamiento con early stopping, validación temporal, guardado a models/*.keras. Predictor carga modelo, predice 7 días, calcula métricas.
  - **Acceptance Criteria:**
    - [ ] Input shape correcto: (None, 21, n_features)
    - [ ] Output: probabilidad de brote (sigmoid) + casos estimados 7 días (ReLU)
    - [ ] Sensibilidad > 75% en validación
    - [ ] Modelo serializado y cargable
    - [ ] Predicciones en rangos válidos (probabilidad [0,1], casos >= 0)
  - **Tests:**
    - [ ] `tests/test_predictor.py`: test_model_shape, test_prediction_range, test_metrics_calculation
    - [ ] Verificar early stopping funciona (loss no diverge)
  - **Complexity:** High

- `[ ]` **TASK-08:** Semilla de Datos + Entrenamiento Inicial
  - **_Boundary_:** `scripts/seed_all.sh`
  - **_Depends_:** TASK-03, TASK-07
  - **Description:** Script seed_all.sh que genera datos sintéticos y entrena los 3 modelos. Pipeline end-to-end verificable con un solo comando.
  - **Acceptance Criteria:**
    - [ ] Un solo comando genera BD poblada + 3 modelos entrenados
    - [ ] Modelos producen predicciones no triviales
  - **Tests:**
    - [ ] Ejecutar `bash scripts/seed_all.sh` y verificar salida sin errores
  - **Complexity:** Low

### Phase D: Web Application

- `[ ]` **TASK-09:** Backend FastAPI — Endpoints REST
  - **_Boundary_:** `src/app.py`
  - **_Depends_:** TASK-02, TASK-07
  - **Description:** Servidor FastAPI con endpoints REST para dashboard, series temporales, mapa de calor, métricas, upload CSV, reentrenamiento.
  - **Acceptance Criteria:**
    - [ ] Endpoints retornan JSON válido
    - [ ] Subida de CSV por multipart funciona
    - [ ] Reentrenamiento se dispara y retorna estado
    - [ ] Tiempo de respuesta < 500ms para endpoints de datos
  - **Tests:**
    - [ ] `tests/test_api.py`: test_get_dashboard, test_get_timeseries, test_get_heatmap, test_upload_csv, test_retrain
  - **Complexity:** High

- `[ ]` **TASK-10:** Frontend Web — Dashboard con Plotly.js
  - **_Boundary_:** `static/index.html`, `static/css/style.css`, `static/js/`
  - **_Depends_:** TASK-09
  - **Description:** Dashboard responsive con selector de enfermedad, series temporales Plotly, mapa de calor SLP (choropleth), polling 60s, indicadores de métricas del modelo.
  - **Acceptance Criteria:**
    - [ ] Dashboard carga en < 3s en navegador moderno
    - [ ] Gráficos se actualizan con polling cada 60s
    - [ ] Mapa de calor muestra 58 municipios coloreados por riesgo
    - [ ] Selector de enfermedad cambia todos los gráficos
  - **Tests:**
    - [ ] Verificar carga visual (manual)
    - [ ] Verificar llamadas AJAX en Network tab
  - **Complexity:** Medium

### Phase E: Presentation & Quality

- `[ ]` **TASK-11:** Presentación LaTeX Beamer
  - **_Boundary_:** `presentacion/presentacion.tex`, `presentacion/presentacion.bib`
  - **_Depends_:** TASK-08
  - **Description:** Presentación LaTeX Beamer del proyecto completo. Portada con datos del expositor, secciones de introducción, objetivos, metodología, arquitectura, resultados, conclusiones. Usa plantillas del harness SDD.
  - **Acceptance Criteria:**
    - [ ] Compila sin errores con `pdflatex` + `bibtex`
    - [ ] Portada con datos correctos del expositor
    - [ ] Incluye diagramas de arquitectura y gráficos
  - **Tests:**
    - [ ] `pdflatex presentacion.tex` sin errores
  - **Complexity:** Low

- `[ ]` **TASK-12:** Calidad — Tests y Quality Gates
  - **_Boundary_:** `tests/`, verificación de quality-gates.json
  - **_Depends_:** TASK-02, TASK-05, TASK-07, TASK-09
  - **Description:** Escribir tests unitarios y de integración completos. Ejecutar ruff, pytest, verificar cobertura. Documentar resultados.
  - **Acceptance Criteria:**
    - [ ] `ruff check src/ tests/` sin errores
    - [ ] Todos los tests de pytest pasan
    - [ ] Cobertura > 70% en módulos core
  - **Tests:**
    - [ ] Ejecutar suite completa de tests
  - **Complexity:** Medium

---

## Progress Summary

| Phase | Total | Done | In Progress | Blocked |
|-------|-------|------|-------------|---------|
| A — Foundation | 3 | 0 | 0 | 0 |
| B — Data Pipeline | 3 | 0 | 0 | 0 |
| C — RNN Model | 2 | 0 | 0 | 0 |
| D — Web Application | 2 | 0 | 0 | 0 |
| E — Presentation & QA | 2 | 0 | 0 | 0 |
| **Total** | **12** | **0** | **0** | **0** |

---

## Blocked Tasks Log

| Task ID | Blocked Since | Reason | Resolution |
|---------|--------------|--------|------------|
| — | — | — | — |
