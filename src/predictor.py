import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Optional

import numpy as np
import tensorflow as tf
from tensorflow import keras

from database import Database
from synthetic_data import MUNICIPALITIES, get_municipality_population_weight

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
SEQUENCE_LENGTH = 21


class Predictor:
    def __init__(self):
        self._models: dict[str, keras.Model] = {}

    def load_model(self, disease: str) -> Optional[keras.Model]:
        if disease in self._models:
            return self._models[disease]

        model_path = MODEL_DIR / f"{disease}_model.keras"
        if not model_path.exists():
            logger.warning(f"Modelo no encontrado: {model_path}")
            return None

        try:
            model = keras.models.load_model(str(model_path))
            self._models[disease] = model
            logger.info(f"Modelo cargado: {disease}")
            return model
        except Exception as e:
            logger.error(f"Error cargando modelo {disease}: {e}")
            return None

    def predict(
        self,
        disease: str,
        sequence_length: int = SEQUENCE_LENGTH,
    ) -> Optional[dict[str, Any]]:
        db = Database()
        model = self.load_model(disease)
        if model is None:
            return None

        n_features = model.input_shape[-1]
        keyword_list = db.get_all_keywords(disease)
        n_kw = len(keyword_list)
        if n_kw + 3 != n_features:
            logger.warning(
                f"Disease {disease}: keywords ({n_kw}+3={n_kw+3}) "
                f"!= model features ({n_features})"
            )
        n_feat = n_kw + 3

        end_date = date.today()
        start_date = end_date - timedelta(days=sequence_length + 10)
        trends = db.get_search_trends(disease, start_date, end_date)
        epi_data = db.get_timeseries(disease, start_date, end_date)

        if len(epi_data) < sequence_length:
            logger.warning(
                f"Se necesitan {sequence_length} datos epidemiologicos, "
                f"se tienen {len(epi_data)}"
            )
            return None

        last_entries = epi_data[-sequence_length:]
        feature_window = np.zeros((1, sequence_length, n_features))

        for i, entry in enumerate(last_entries):
            d = entry["date"]
            if isinstance(d, str):
                from datetime import datetime
                d = datetime.strptime(d, "%Y-%m-%d").date()

            for ki, kw in enumerate(keyword_list):
                matching = [t for t in trends if t["keyword"] == kw and t["date"] == d]
                val = matching[0]["value"] if matching else 0.0
                feature_window[0, i, ki] = val

            cases = float(entry["confirmed_cases"])
            hosp = float(entry["hospitalizations"])
            deaths = float(entry["deaths"])
            feature_window[0, i, n_kw] = cases / 100.0
            feature_window[0, i, n_kw + 1] = hosp / 20.0
            feature_window[0, i, n_kw + 2] = deaths / 5.0

        prob_out, cases_out = model.predict(feature_window, verbose=0)

        outbreak_prob = float(prob_out[0, 0])
        estimated_cases_7d = float(cases_out[0, 0])
        std_est = estimated_cases_7d * 0.3

        return {
            "disease": disease,
            "prediction_date": date.today().isoformat(),
            "outbreak_probability": round(outbreak_prob, 4),
            "estimated_cases_7d": round(estimated_cases_7d, 2),
            "ci_lower": round(max(0, estimated_cases_7d - 2 * std_est), 2),
            "ci_upper": round(estimated_cases_7d + 2 * std_est, 2),
        }

    def predict_all(
        self,
    ) -> dict[str, Optional[dict[str, Any]]]:
        results = {}
        for disease in ["hantavirus", "covid", "dengue"]:
            try:
                result = self.predict(disease)
                results[disease] = result
            except Exception as e:
                logger.error(f"Error prediciendo {disease}: {e}")
                results[disease] = None
        return results
