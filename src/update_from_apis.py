#!/usr/bin/env python3
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from datetime import date, datetime
from database import Database
from data_sources.google_trends import GoogleTrendsClient
from data_sources.government_apis import fetch_from_all_sources

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("update_from_apis")


def run_pipeline(
    db: Database,
    days_back: int = 90,
    force_retrain: bool = False,
) -> dict[str, bool]:
    results: dict[str, bool] = {}

    logger.info("=== Iniciando pipeline diario ===")

    # Step 1: Google Trends
    logger.info("Paso 1: Extrayendo Google Trends...")
    trends_client = GoogleTrendsClient()
    try:
        trends_data = trends_client.fetch_all_diseases(days_back=days_back)
        if trends_data:
            for entry in trends_data:
                db.insert_search_trend(entry)
            results["google_trends"] = True
            logger.info(f"Google Trends: {len(trends_data)} registros insertados")
        else:
            results["google_trends"] = False
            logger.warning("Google Trends: sin datos obtenidos")
    except Exception as e:
        results["google_trends"] = False
        logger.error(f"Google Trends: error - {e}")

    # Step 2: Government APIs
    logger.info("Paso 2: Intentando fuentes gubernamentales...")
    end = date.today()
    start = date(2024, 1, 1)
    all_gov_data: list[dict] = []
    for disease in ["hantavirus", "covid", "dengue"]:
        gov_data = fetch_from_all_sources(disease, start, end)
        if gov_data:
            for entry in gov_data:
                db.insert_epidemiological({
                    "date": entry.get("date", start),
                    "disease": disease,
                    "municipality": entry.get("municipality", "Desconocido"),
                    "confirmed_cases": int(entry.get("confirmed_cases", 0)),
                    "hospitalizations": int(entry.get("hospitalizations", 0)),
                    "deaths": int(entry.get("deaths", 0)),
                    "source": entry.get("_source", "api"),
                })
            all_gov_data.extend(gov_data)

    results["government_apis"] = len(all_gov_data) > 0
    if all_gov_data:
        logger.info(f"Gobierno: {len(all_gov_data)} registros insertados")
    else:
        logger.warning("Gobierno: ninguna fuente disponible")

    # Step 3: Auto-retrain on Sunday or force
    today = date.today()
    should_retrain = force_retrain or (today.weekday() == 6)
    results["retrained"] = False

    if should_retrain:
        logger.info("Paso 3: Reentrenando modelos (domingo o forzado)...")
        try:
            from train_model import train_disease_model

            for disease in ["hantavirus", "covid", "dengue"]:
                logger.info(f"Entrenando modelo para {disease}...")
                metrics = train_disease_model(disease, db)
                db.insert_model_metrics(metrics)
                results["retrained"] = True
            logger.info("Reentrenamiento completado")
        except Exception as e:
            logger.error(f"Error en reentrenamiento: {e}")
    else:
        logger.info("Paso 3: Saltando reentrenamiento (no es domingo ni forzado)")

    logger.info("=== Pipeline diario completado ===")
    return results


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Pipeline diario de actualizacion de datos"
    )
    parser.add_argument(
        "--days-back", type=int, default=90,
        help="Dias hacia atras para Google Trends (default: 90)"
    )
    parser.add_argument(
        "--force-retrain", action="store_true",
        help="Forzar reentrenamiento de modelos"
    )
    args = parser.parse_args()

    db = Database()
    results = run_pipeline(
        db,
        days_back=args.days_back,
        force_retrain=args.force_retrain,
    )
    print(f"Resultados: {results}")


if __name__ == "__main__":
    main()
