# Specification: SPEC-001 — Sistema de Predicción de Enfermedades con RNN

> **Status:** Under Review
> **Author:** Sistema SDD
> **Date:** 2026-05-24
> **Approved by:** _Pending_

---

## 1. Summary / Resumen

**Problem:**
El estado de San Luis Potosí (SLP), México, enfrenta brotes periódicos de enfermedades infecciosas como hantavirus, COVID-19 y dengue. No existe un sistema integrado que combine datos de tendencias de búsqueda (Google Trends), datos epidemiológicos oficiales y observaciones clínicas para predecir brotes con antelación. Las fuentes gubernamentales no siempre están disponibles, y no hay mecanismos de actualización manual robustos.

**Proposed Solution:**
Un sistema de predicción basado en redes neuronales RNN (LSTM/GRU) que:
- Extrae datos diarios de Google Trends para keywords locales de cada enfermedad
- Integra datos epidemiológicos de fuentes gubernamentales mexicanas (con fallback a CSV manual)
- Permite a administradores cargar CSVs manualmente cuando las APIs fallen
- Permite a médicos registrar observaciones mediante Google Forms
- Entrena modelos RNN por enfermedad para predecir brotes a 7 días
- Despliega un dashboard web en tiempo real con FastAPI + Plotly.js
- Se reentrena automáticamente cada semana o manualmente tras carga de datos

---

## 2. Actors / Stakeholders

| Actor | Description | Role |
|-------|-------------|------|
| Administrador del sistema | Personal de salud pública que opera el sistema | Carga CSVs manuales, monitorea pipelines, lanza reentrenamiento, configura fuentes |
| Médico / Epidemiólogo | Personal clínico que registra observaciones de pacientes | Ingresa datos de casos via Google Forms (tipo de hantavirus, síntomas, diagnóstico de dengue) |
| Visitante / Tomador de decisiones | Usuario final que consulta dashboards y predicciones | Visualiza mapas de calor, series temporales, probabilidades de brote sin autenticación |
| Sistema automático | Pipeline diario | Ejecuta `update_from_apis.py` (cron), entrena modelo semanalmente |
| Fuentes externas | Google Trends, APIs de Datos Abiertos México, SINAIS, Google Sheets | Proveen datos crudos |

---

## 3. Functional Requirements

### 3.1. Core Requirements

- **FR-01:** El sistema **MUST** extraer datos diarios de Google Trends (pytrends) para México y SLP con las keywords definidas para hantavirus, COVID-19, y dengue.
- **FR-02:** El sistema **MUST** intentar acceder a fuentes gubernamentales mexicanas (Datos Abiertos México, SINAIS, boletines SLP) en cada ejecución del pipeline diario.
- **FR-03:** Si una fuente externa falla o no está disponible, el sistema **MUST** permitir la carga manual de archivos CSV por el administrador.
- **FR-04:** El sistema **MUST** incluir un script `import_csv.py` que lea CSVs con formato definido (fecha, municipio, enfermedad, casos, hospitalizaciones, muertes) y los inserte en la BD.
- **FR-05:** El sistema **MUST** almacenar todos los datos en una base de datos SQL (SQLite por defecto, PostgreSQL opcional).
- **FR-06:** El sistema **MUST** incluir un modelo RNN (LSTM o GRU) por enfermedad usando TensorFlow/Keras.
- **FR-07:** El modelo **MUST** usar una ventana de entrada de 21 días de tendencias + casos históricos y predecir probabilidad de brote y casos estimados para los próximos 7 días.
- **FR-08:** El sistema **MUST** soportar reentrenamiento semanal automático y reentrenamiento manual invocado por el administrador.
- **FR-09:** El sistema **MUST** proporcionar un dashboard web vía FastAPI con Plotly.js que muestre:
  - Mapa de calor de SLP por municipio para cada enfermedad
  - Series temporales de casos reales vs predichos
  - Probabilidad de brote para los próximos 7 días
- **FR-10:** El dashboard **MUST** consultar la BD directamente en cada carga y actualizarse mediante polling AJAX cada 60 segundos.
- **FR-11:** El sistema **SHOULD** integrar Google Forms en fase 2 para que médicos registren observaciones clínicas, leyendo respuestas via Google Sheets API (gspread). En fase 1 no se implementa.
- **FR-12:** El sistema **MAY** ser extensible a enfermedades adicionales (leishmaniasis, rickettsiosis) mediante configuración.
- **FR-13:** El administrador **MAY** subir archivos CSV desde la interfaz web (autenticación básica requerida).
- **FR-14:** El sistema **MUST** generar datos sintéticos realistas para inicializar la BD y permitir demostraciones sin datos reales.
- **FR-15:** El sistema **MUST** calcular y mostrar métricas del modelo: sensibilidad (>75%), especificidad, RMSE, precisión.
- **FR-16:** El proyecto **MUST** incluir una presentación académica en LaTeX Beamer que explique la arquitectura, metodología, resultados y conclusiones del sistema.

### 3.2. Keywords por Enfermedad

**Hantavirus:**
"tos", "fiebre", "dolor muscular", "dificultad para respirar", "sangrado", "ratón de campo", "hantavirus síntomas"

**COVID-19:**
"covid tos", "covid fiebre", "pérdida de olfato", "covid México", "covid SLP"

**Dengue:**
"dengue fiebre", "dolor de huesos", "sarpullido", "dengue SLP", "mosquito"

### 3.3. Input / Output

**Inputs:**
| Input | Type | Source | Validation |
|-------|------|--------|------------|
| Google Trends data | JSON/CSV | pytrends API (diario) | Fechas válidas, región MX/SLP |
| Datos epidemiológicos | JSON/CSV | APIs gobierno mexicano | Formato esperado o fallback |
| CSV manual | CSV | Administrador (upload o CLI) | Columnas: fecha, municipio, enfermedad, casos, hospitalizaciones, muertes |
| Observaciones clínicas | Google Sheets row | Google Forms → Google Sheets | Campos específicos por enfermedad |
| Parámetros de entrenamiento | Config | Administrador / default | learning_rate, epochs, batch_size |

**Outputs:**
| Output | Type | Destination | Format |
|--------|------|-------------|--------|
| Predicciones 7 días | JSON | Dashboard web | {fecha, enfermedad, municipio, prob_brote, casos_estimados, ic_inf, ic_sup} |
| Series temporales | JSON | Dashboard web | {fechas, casos_reales, casos_predichos, tendencias} |
| Mapa de calor | GeoJSON + valores | Dashboard web (Plotly) | {municipio, lat, lon, riesgo} |
| Métricas del modelo | JSON | Dashboard web | {sensibilidad, especificidad, rmse, precision, fecha_entrenamiento} |

---

## 4. Non-Functional Requirements

- **NFR-01 (Performance):** La página web **MUST** cargar gráficos en menos de 3 segundos en conexiones de banda ancha.
- **NFR-02 (Performance):** El polling AJAX **SHOULD** completar en menos de 1 segundo.
- **NFR-03 (Reliability):** El sistema **MUST** funcionar completamente sin conexión a APIs externas (usando solo carga manual de CSVs).
- **NFR-04 (Portability):** El sistema **MUST** funcionar con SQLite (sin necesidad de PostgreSQL) para desarrollo local.
- **NFR-05 (Accuracy):** El modelo RNN **MUST** alcanzar sensibilidad > 75% en datos de validación.
- **NFR-06 (Maintainability):** El código **MUST** estar organizado en scripts separados: `update_from_apis.py`, `import_csv.py`, `train_model.py`, `app.py`.
- **NFR-07 (Security):** No se requiere autenticación en fase 1 (entorno local/demostración). La carga de CSVs está disponible sin login.
- **NFR-08 (Data Freshness):** Los cambios de datos (carga manual de CSV) **MUST** reflejarse en la web inmediatamente (al refrescar o dentro de 60s por polling).

---

## 5. Acceptance Criteria

- **AC-01:** Given un CSV con formato válido (fecha, municipio, enfermedad, casos), when ejecuto `python import_csv.py datos.csv`, then los datos se insertan en la BD y aparecen en el dashboard al refrescar.
- **AC-02:** Given el sistema sin conexión a internet, when ejecuto `python import_csv.py datos.csv`, then los datos se cargan exitosamente y la web funciona completamente.
- **AC-03:** Given datos históricos de 90+ días, when ejecuto `python train_model.py`, then el modelo se entrena, las métricas se guardan, y la web muestra sensibilidad > 75%.
- **AC-04:** Given el dashboard abierto en un navegador, when la página carga completamente, then los gráficos se renderizan en menos de 3 segundos.
- **AC-05:** Given el pipeline diario configurado con cron, when se ejecuta `update_from_apis.py`, then los datos de Google Trends se actualizan y los modelos se reentrenan si es domingo.
- **AC-06:** Given un administrador autenticado, when sube un CSV via interfaz web, then los datos se importan y el dashboard refleja los cambios inmediatamente.
- **AC-07:** Given la BD poblada con datos sintéticos, when se navega al dashboard de hantavirus, then se muestra mapa de calor de SLP con municipios coloreados por riesgo y serie temporal con predicciones.

---

## 6. Constraints and Assumptions

### Constraints
- Python 3.10+ obligatorio
- SQLite como BD por defecto (PostgreSQL opcional como reemplazo directo)
- TensorFlow/Keras para modelos RNN
- FastAPI para backend web
- Plotly.js para visualizaciones frontend
- Los scripts deben ejecutarse independientemente (no monolito)

### Assumptions
- El usuario tiene Python 3.10+ instalado
- pytrends puede requerir una conexión a internet funcional
- Las APIs gubernamentales pueden no estar siempre disponibles
- Google Sheets API requiere configuración de credenciales (opcional)
- Se generarán datos sintéticos realistas para la demostración inicial
- Los 58 municipios de SLP serán representados en el mapa de calor
- El cron job para el pipeline diario se configurará manualmente por el administrador

---

## 7. Resolved Questions

- **Q1:** ExactTrend — Se usará el término exacto de búsqueda (más estable para modelos ML).
- **Q2:** Sin autenticación — Dashboards públicos (solo lectura), apto para entorno local/demostración.
- **Q3:** Google Forms se implementará en fase 2 (posterior). La fase 1 se enfoca en pipeline, modelo y dashboard.
- **Q4:** Todos los 58 municipios de SLP serán representados en el mapa de calor.
- **Q5:** Un solo administrador en fase 1. Extensible en el futuro.

---

## 8. Diagrams

### Arquitectura de Datos

```
                    ┌─────────────────────┐
                    │   Google Trends API  │
                    │     (pytrends)       │
                    └─────────┬───────────┘
                              │
                    ┌─────────▼───────────┐
                    │  update_from_apis   │
                    │       .py           │
                    └────┬──────┬─────────┘
                         │      │
              ┌──────────▼┐  ┌──▼──────────────┐
              │ APIs Gob. │  │  import_csv.py   │
              │ (fallback)│  │  (carga manual)  │
              └──────────┘  └──┬───────────────┘
                               │
                    ┌──────────▼───────────┐
                    │   SQLite/PostgreSQL   │
                    │   (BD Principal)     │
                    └────┬──────────┬──────┘
                         │          │
              ┌──────────▼┐  ┌──────▼──────────┐
              │train_model│  │  app.py          │
              │   .py     │  │  (FastAPI +      │
              │ (LSTM/MU) │  │   Plotly.js)     │
              └──────────┘  └──────────────────┘
```

### Flujo de Importación Manual

```
Usuario ──► CSV archivo ──► import_csv.py ──► Valida formato
                                                    │
                                          ┌─────────▼─────────┐
                                          │ ¿Formato válido?   │
                                          └─────┬──────┬──────┘
                                           Sí   │      │  No
                                        ┌──────▼┐  ┌──▼───────┐
                                        │Insertar│  │ Error +  │
                                        │   BD   │  │ mensaje  │
                                        └───┬────┘  └──────────┘
                                            │
                                    ┌───────▼───────┐
                                    │ ¿Reentrenar?   │
                                    │ (opcional,     │
                                    │  preguntar)    │
                                    └───────┬───────┘
                                            │
                                  ┌─────────▼─────────┐
                                  │ train_model.py     │
                                  │ (si el usuario     │
                                  │  acepta)           │
                                  └───────────────────┘
```

### Flujo RNN

```
Input (21 días):
┌─────────────────────────────────────────────┐
│ Tendencia keywords día -20 a día 0          │
│ Casos históricos día -20 a día 0            │
│ Hospitalizaciones día -20 a día 0           │
│ Municipio (one-hot encoding)                │
│ Estacionalidad (mes, día de semana)         │
└─────────────────────┬───────────────────────┘
                      │
              ┌───────▼───────┐
              │ LSTM / GRU    │
              │ (2-3 capas)   │
              │ Dropout 0.3   │
              └───────┬───────┘
                      │
              ┌───────▼───────┐
              │ Dense + Sigmoid│ → Probabilidad de brote
              │ Dense + ReLU   │ → Casos estimados (7 días)
              └───────────────┘
```

---

## 9. References

- Google Trends API: https://github.com/GeneralMills/pytrends
- FastAPI: https://fastapi.tiangolo.com/
- TensorFlow/Keras LSTM: https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM
- Plotly.js: https://plotly.com/javascript/
- Datos Abiertos México: https://datos.gob.mx/
- SINAIS: https://www.sinave.gob.mx/
- Google Sheets API (gspread): https://docs.gspread.org/
- San Luis Potosí municipios: https://www.slp.gob.mx/
