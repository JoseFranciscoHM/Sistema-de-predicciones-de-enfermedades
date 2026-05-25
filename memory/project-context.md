# Project Context

## Project Overview

**Name:** Prediccion de Enfermedades SLP - RNN

**Objective:**
Sistema completo de predicción de enfermedades basado en redes neuronales RNN (LSTM/GRU) para el estado de San Luis Potosí, México. El sistema integra Google Trends, datos epidemiológicos gubernamentales, y observaciones clínicas para predecir brotes de hantavirus, COVID-19, dengue y enfermedades extensibles (leishmaniasis, rickettsiosis). Incluye importación manual de CSV como fallback de APIs, reentrenamiento automático/semiautomático del modelo, y dashboard web en tiempo real.

**Current State:**
Nuevo proyecto. No existe código ni datos previos. Se generarán datos sintéticos realistas para demostración y pruebas.

---

## Architecture Summary

Sistema de 4 capas:
1. **Data Layer**: Fuentes externas (pytrends, APIs gobierno) + importación manual CSV + BD SQLite/PostgreSQL
2. **Model Layer**: RNN (LSTM/GRU) con TensorFlow/Keras, reentrenamiento semanal o manual
3. **Backend Layer**: FastAPI con endpoints REST, scheduler interno, autenticación básica
4. **Frontend Layer**: HTML/CSS/JS con Plotly.js, dashboards por enfermedad, polling cada 60s

```
[Google Trends] ──┐
[Gobierno APIs] ──┼──► [Pipeline Datos] ──► [SQLite/PostgreSQL] ◄── [import_csv.py]
[CSV Manual]   ──┘                              │
                                                 ▼
[Doctor Forms] ──► [Google Sheets] ──► [FastAPI] ──► [RNN Model] ──► [Predicciones]
                                                 │
                                                 ▼
                                         [Frontend Plotly.js]
```

---

## Key Components

| Component | Description | Status |
|-----------|-------------|--------|
| update_from_apis.py | Pipeline diario: pytrends + APIs gobierno | New |
| import_csv.py | Importación manual de CSV a BD | New |
| train_model.py | Entrenamiento/Reentrenamiento de RNN | New |
| app.py | Servidor FastAPI + frontend web | New |
| models/ | Modelos RNN serializados (.keras) | New |
| data/ | BD SQLite, CSVs de ejemplo, datos sintéticos | New |

---

## External Dependencies

| Dependency | Purpose | Version |
|-----------|---------|---------|
| Python | Runtime principal | 3.10+ |
| TensorFlow | RNN LSTM/GRU | 2.x |
| FastAPI | Backend web | 0.x |
| pandas | Manipulación de datos | 2.x |
| pytrends | Google Trends API | latest |
| Plotly.js | Gráficos frontend | latest |
| gspread | Google Sheets API (opcional) | latest |
| scikit-learn | Métricas de evaluación | 1.x |

---

## Constraints

- Python 3.10+ como runtime principal
- SQLite para desarrollo local; PostgreSQL opcional para producción
- Las APIs gubernamentales pueden fallar → sistema debe funcionar con CSV manual
- Dashboard web debe cargar gráficos en < 3 segundos
- Modelo RNN debe tener sensibilidad > 75%
- Datos sintéticos iniciales para demostración

---

## Notes

- Framework DL seleccionado: TensorFlow/Keras
- Framework web seleccionado: FastAPI
- No hay datos históricos reales disponibles → generar datos sintéticos
- Google Forms + Google Sheets como integración opcional para doctores
