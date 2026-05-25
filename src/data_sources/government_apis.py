import logging
from datetime import date, timedelta
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

GOVERNMENT_API_TIMEOUT = 10


def fetch_from_datos_mexico(
    disease: str, start_date: date, end_date: date
) -> list[dict[str, Any]]:
    logger.info(
        f"Intentando Datos Abiertos Mexico: disease={disease}, "
        f"{start_date} - {end_date}"
    )
    try:
        resp = requests.get(
            "https://api.datos.gob.mx/v1/condition",  # placeholder URL
            params={"disease": disease, "from": start_date.isoformat(),
                    "to": end_date.isoformat()},
            timeout=GOVERNMENT_API_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        records = data.get("results", [])
        logger.info(f"Datos Abiertos Mexico: {len(records)} registros")
        return records
    except requests.RequestException as e:
        logger.warning(f"Datos Abiertos Mexico no disponible: {e}")
        return []
    except Exception as e:
        logger.exception(f"Error inesperado en API gobierno: {e}")
        return []


def fetch_from_sinais(
    disease: str, start_date: date, end_date: date
) -> list[dict[str, Any]]:
    logger.info(
        f"Intentando SINAIS: disease={disease}, "
        f"{start_date} - {end_date}"
    )
    try:
        resp = requests.get(
            "https://www.sinave.gob.mx/api/reports",  # placeholder URL
            params={"disease": disease, "start": start_date.isoformat(),
                    "end": end_date.isoformat()},
            timeout=GOVERNMENT_API_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        records = data if isinstance(data, list) else data.get("data", [])
        logger.info(f"SINAIS: {len(records)} registros")
        return records
    except requests.RequestException as e:
        logger.warning(f"SINAIS no disponible: {e}")
        return []
    except Exception as e:
        logger.exception(f"Error inesperado en SINAIS: {e}")
        return []


def fetch_from_all_sources(
    disease: str, start_date: date, end_date: date
) -> list[dict[str, Any]]:
    all_records: list[dict[str, Any]] = []

    for source_name, source_fn in [
        ("Datos Abiertos Mexico", fetch_from_datos_mexico),
        ("SINAIS", fetch_from_sinais),
    ]:
        records = source_fn(disease, start_date, end_date)
        if records:
            for r in records:
                r["_source"] = source_name
            all_records.extend(records)
            logger.info(f"{source_name}: {len(records)} registros obtenidos")

    if not all_records:
        logger.warning(
            "NINGUNA fuente gubernamental disponible. "
            "Usar import_csv.py para carga manual."
        )

    return all_records
