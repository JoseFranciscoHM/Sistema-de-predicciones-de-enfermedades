import json
import logging
import os
import sys
import tempfile
import threading
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

import atexit
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import pandas as pd

from database import Database
from predictor import Predictor
from synthetic_data import MUNICIPALITIES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "database.db"

# --- Inicializacion al arrancar ---
os.makedirs(Path(DB_PATH).parent, exist_ok=True)
os.makedirs(Path(DB_PATH).parent.parent / "models", exist_ok=True)

db_init = Database(str(DB_PATH))

if not Path(DB_PATH).exists() or os.path.getsize(DB_PATH) < 4096:
    logger.info("Generando datos sinteticos iniciales...")
    from synthetic_data import generate_all_synthetic_data
    generate_all_synthetic_data(db_init)
    logger.info("Datos sinteticos generados exitosamente")

    def _train_all():
        import subprocess
        base = Path(__file__).resolve().parent.parent
        for disease in ["dengue", "hantavirus", "covid"]:
            model_path = base / "models" / f"{disease}_model.keras"
            if not model_path.exists():
                logger.info(f"Entrenando modelo {disease}...")
                subprocess.run(
                    [sys.executable, str(base / "src" / "train_model.py"), "--disease", disease, "--epochs", "2"],
                    cwd=str(base),
                    env={**os.environ, "PYTHONPATH": str(base / "src")},
                    capture_output=True,
                )
                logger.info(f"Modelo {disease} entrenado")

    thread = threading.Thread(target=_train_all, daemon=True)
    thread.start()

db_init.close()

app = FastAPI(title="Prediccion de Enfermedades SLP", version="1.0")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

db = Database(str(DB_PATH))
predictor = Predictor()

DISEASE_NAMES = {
    "hantavirus": "Hantavirus",
    "covid": "COVID-19",
    "dengue": "Dengue",
}

DISEASE_COLORS = {
    "hantavirus": "#e74c3c",
    "covid": "#3498db",
    "dengue": "#f39c12",
}


@app.get("/", response_class=HTMLResponse)
async def root():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text())
    return HTMLResponse("<h1>Prediccion de Enfermedades SLP</h1><p>Frontend no encontrado</p>")


@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/api/diseases")
async def list_diseases():
    return DISEASE_NAMES


@app.get("/api/dashboard/{disease}")
async def get_dashboard(disease: str):
    if disease not in DISEASE_NAMES:
        raise HTTPException(404, f"Enfermedad '{disease}' no encontrada")

    end = date.today()
    start = end - timedelta(days=365)

    timeseries = db.get_timeseries(disease, start, end)
    municipality_data = db.get_municipality_data(disease, start, end)
    metrics = db.get_latest_metrics(disease)
    prediction = predictor.predict(disease)

    return {
        "disease": disease,
        "disease_name": DISEASE_NAMES[disease],
        "color": DISEASE_COLORS[disease],
        "timeseries": timeseries,
        "municipality_data": municipality_data,
        "metrics": metrics,
        "prediction": prediction,
    }


@app.get("/api/timeseries/{disease}")
async def get_timeseries(
    disease: str,
    days: int = Query(365, description="Dias hacia atras"),
):
    if disease not in DISEASE_NAMES:
        raise HTTPException(404, f"Enfermedad '{disease}' no encontrada")

    end = date.today()
    start = end - timedelta(days=days)
    data = db.get_timeseries(disease, start, end)
    return {"disease": disease, "data": data}


@app.get("/api/search-trends/{disease}")
async def get_search_trends(
    disease: str,
    days: int = Query(365, description="Dias hacia atras"),
):
    if disease not in DISEASE_NAMES:
        raise HTTPException(404, f"Enfermedad '{disease}' no encontrada")

    end = date.today()
    start = end - timedelta(days=days)
    data = db.get_search_trends(disease, start, end)

    keywords_seen: set[str] = set()
    series: list[dict] = []
    for row in data:
        kw = row["keyword"]
        if kw not in keywords_seen:
            keywords_seen.add(kw)

    for kw in sorted(keywords_seen):
        points = [r for r in data if r["keyword"] == kw]
        points.sort(key=lambda r: r["date"])
        series.append({
            "keyword": kw,
            "data": points,
        })

    return {
        "disease": disease,
        "disease_name": DISEASE_NAMES[disease],
        "keywords": sorted(keywords_seen),
        "series": series,
    }


@app.get("/api/heatmap/{disease}")
async def get_heatmap(disease: str, days: int = Query(90, description="Dias hacia atras")):
    if disease not in DISEASE_NAMES:
        raise HTTPException(404, f"Enfermedad '{disease}' no encontrada")

    end = date.today()
    start = end - timedelta(days=days)
    data = db.get_municipality_data(disease, start, end)

    # Ensure all 58 municipalities are present
    present = {r["municipality"] for r in data}
    for m in MUNICIPALITIES:
        if m not in present:
            data.append({
                "municipality": m,
                "total_cases": 0,
                "total_hosp": 0,
                "total_deaths": 0,
            })

    data.sort(key=lambda r: r["municipality"])
    return {"disease": disease, "municipalities": data}


@app.get("/api/metrics/{disease}")
async def get_metrics(disease: str):
    if disease not in DISEASE_NAMES:
        raise HTTPException(404, f"Enfermedad '{disease}' no encontrada")

    metrics = db.get_latest_metrics(disease)
    if metrics is None:
        return {"disease": disease, "metrics": None, "message": "Modelo no entrenado"}
    return {"disease": disease, "metrics": metrics}


class CaseSubmission(BaseModel):
    disease: str = Field(..., description="dengue, hantavirus o covid")
    municipality: str = Field(..., min_length=1)
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    confirmed_cases: int = Field(default=0, ge=0)
    hospitalizations: int = Field(default=0, ge=0)
    deaths: int = Field(default=0, ge=0)
    reporter_name: str = Field(default="", max_length=200)
    symptoms: str = Field(default="", description="Sintomas separados por coma")
    hantavirus_type: str = Field(default="", description="Tipo de hantavirus (Andes, Sin Nombre, etc.)")
    dengue_severity: str = Field(default="", description="Gravedad del dengue (sin signos de alarma, con signos de alarma, grave)")
    auto_retrain: bool = Field(default=False, description="Reentrenar modelo automaticamente")


@app.post("/api/cases")
async def submit_case(case: CaseSubmission):
    if case.disease not in DISEASE_NAMES:
        raise HTTPException(400, f"Enfermedad invalida: {case.disease}")
    if case.municipality not in MUNICIPALITIES:
        raise HTTPException(400, f"Municipio invalido: {case.municipality}")

    db.insert_epidemiological({
        "date": case.date,
        "disease": case.disease,
        "municipality": case.municipality,
        "confirmed_cases": case.confirmed_cases,
        "hospitalizations": case.hospitalizations,
        "deaths": case.deaths,
        "source": "doctor",
    })

    if case.symptoms or case.hantavirus_type or case.dengue_severity:
        db.insert_clinical_data({
            "date": case.date,
            "disease": case.disease,
            "municipality": case.municipality,
            "hantavirus_type": case.hantavirus_type or None,
            "dengue_severity": case.dengue_severity or None,
            "symptoms": case.symptoms or None,
        })

    logger.info(
        f"Caso documentado por {case.reporter_name or 'anonimo'}: "
        f"{case.disease} en {case.municipality} el {case.date} "
        f"(sintomas: {case.symptoms or 'ninguno'})"
    )

    if case.auto_retrain:
        _trigger_retrain(case.disease)
        return {"status": "ok", "message": "Caso registrado exitosamente. Reentrenamiento iniciado."}

    return {"status": "ok", "message": "Caso registrado exitosamente"}


def _trigger_retrain(disease: str):
    def _train():
        try:
            from train_model import train_disease_model
            db2 = Database(str(DB_PATH))
            metrics = train_disease_model(disease, db2)
            db2.insert_model_metrics(metrics)
            logger.info(f"Reentrenamiento completado para {disease}: {metrics}")
        except Exception as e:
            logger.error(f"Error en reentrenamiento de {disease}: {e}")

    thread = threading.Thread(target=_train, daemon=True)
    thread.start()


@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")

    try:
        from import_csv import import_csv_string
        result = import_csv_string(text, db)
        return {
            "status": "success" if result["errors"] == 0 else "partial",
            "inserted": result["inserted"],
            "errors": result["errors"],
        }
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.exception("Error en upload CSV")
        raise HTTPException(500, f"Error interno: {e}")


@app.post("/api/retrain/{disease}")
async def retrain_model(disease: str):
    if disease not in DISEASE_NAMES:
        raise HTTPException(404, f"Enfermedad '{disease}' no encontrada")

    _trigger_retrain(disease)

    return {
        "status": "started",
        "disease": disease,
        "message": "Reentrenamiento iniciado en segundo plano",
    }


@app.get("/api/predictions/{disease}")
async def get_predictions(disease: str):
    if disease not in DISEASE_NAMES:
        raise HTTPException(404, f"Enfermedad '{disease}' no encontrada")

    prediction = predictor.predict(disease)
    if prediction is None:
        return {"disease": disease, "prediction": None}

    return {"disease": disease, "prediction": prediction}


@app.get("/api/keywords/{disease}")
async def list_keywords(disease: str):
    if disease not in DISEASE_NAMES:
        raise HTTPException(404, f"Enfermedad '{disease}' no encontrada")
    base = db.get_all_keywords(disease)
    overrides = db.get_keyword_overrides(disease)
    return {
        "disease": disease,
        "keywords": base,
        "overrides": overrides,
    }


@app.post("/api/keywords/{disease}")
async def add_keyword(disease: str, body: dict = ...):
    if disease not in DISEASE_NAMES:
        raise HTTPException(404, f"Enfermedad '{disease}' no encontrada")
    keyword = body.get("keyword", "").strip().lower()
    if not keyword:
        raise HTTPException(400, "Keyword vacio")
    if len(keyword) > 100:
        raise HTTPException(400, "Keyword demasiado larga (max 100)")

    db.add_keyword_override(disease, keyword)

    from synthetic_data import KEYWORDS
    base = KEYWORDS.get(disease, [])
    all_kw = list(base)
    if keyword not in all_kw:
        all_kw.append(keyword)

    return {
        "status": "ok",
        "keyword": keyword,
        "disease": disease,
        "keywords": all_kw,
        "overrides": db.get_keyword_overrides(disease),
    }


@app.delete("/api/keywords/{disease}")
async def remove_keyword(disease: str, body: dict = ...):
    if disease not in DISEASE_NAMES:
        raise HTTPException(404, f"Enfermedad '{disease}' no encontrada")
    keyword = body.get("keyword", "").strip().lower()
    if not keyword:
        raise HTTPException(400, "Keyword vacio")

    db.remove_keyword_override(disease, keyword)

    from synthetic_data import KEYWORDS
    base = KEYWORDS.get(disease, [])
    all_kw = list(base) + db.get_keyword_overrides(disease)

    return {
        "status": "ok",
        "keyword": keyword,
        "disease": disease,
        "keywords": all_kw,
        "overrides": db.get_keyword_overrides(disease),
    }


@app.post("/api/update-keywords/{disease}")
async def update_keywords_and_retrain(disease: str, body: dict = ...):
    if disease not in DISEASE_NAMES:
        raise HTTPException(404, f"Enfermedad '{disease}' no encontrada")

    keywords = body.get("keywords", [])
    if not isinstance(keywords, list) or len(keywords) == 0:
        raise HTTPException(400, "Se requiere una lista de keywords")

    db._execute("DELETE FROM keyword_overrides WHERE disease = ?", (disease,))
    for kw in keywords:
        db._execute(
            "INSERT OR IGNORE INTO keyword_overrides (disease, keyword) VALUES (?, ?)",
            (disease, kw.lower().strip()),
        )
    db._connect().commit()

    _trigger_retrain(disease)

    return {
        "status": "started",
        "disease": disease,
        "keywords": db.get_all_keywords(disease),
        "message": "Keywords actualizadas. Reentrenamiento iniciado.",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
