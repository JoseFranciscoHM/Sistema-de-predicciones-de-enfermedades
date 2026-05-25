#!/usr/bin/env python3
import argparse
import csv
import logging
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from database import Database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "date", "municipality", "disease",
    "confirmed_cases", "hospitalizations", "deaths",
]


def validate_row(row: dict[str, str], line_num: int) -> Optional[dict[str, Any]]:
    errors: list[str] = []

    try:
        parsed_date = datetime.strptime(row.get("date", ""), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        errors.append(f"Linea {line_num}: fecha invalida '{row.get('date')}' (use YYYY-MM-DD)")
        parsed_date = None

    municipality = (row.get("municipality") or "").strip()
    if not municipality:
        errors.append(f"Linea {line_num}: municipio vacio")

    disease = (row.get("disease") or "").strip().lower()
    if disease not in ("hantavirus", "covid", "dengue"):
        errors.append(f"Linea {line_num}: enfermedad desconocida '{disease}'")

    try:
        confirmed = int(row.get("confirmed_cases", 0))
        if confirmed < 0:
            errors.append(f"Linea {line_num}: casos confirmados negativo")
    except (ValueError, TypeError):
        errors.append(f"Linea {line_num}: casos confirmados invalido")
        confirmed = 0

    try:
        hospitalizations = int(row.get("hospitalizations", 0))
        if hospitalizations < 0:
            errors.append(f"Linea {line_num}: hospitalizaciones negativo")
    except (ValueError, TypeError):
        errors.append(f"Linea {line_num}: hospitalizaciones invalido")
        hospitalizations = 0

    try:
        deaths = int(row.get("deaths", 0))
        if deaths < 0:
            errors.append(f"Linea {line_num}: muertes negativo")
    except (ValueError, TypeError):
        errors.append(f"Linea {line_num}: muertes invalido")
        deaths = 0

    if errors:
        for e in errors:
            logger.error(e)
        return None

    return {
        "date": parsed_date,
        "municipality": municipality,
        "disease": disease,
        "confirmed_cases": confirmed,
        "hospitalizations": hospitalizations,
        "deaths": deaths,
        "source": "csv",
    }


def import_csv_string(
    csv_content: str, db: Optional[Database] = None
) -> dict[str, int]:
    if db is None:
        db = Database()
    reader = csv.DictReader(csv_content.splitlines())
    missing = [c for c in EXPECTED_COLUMNS if c not in reader.fieldnames]
    if missing:
        raise ValueError(
            f"Columnas faltantes en CSV: {missing}. "
            f"Esperadas: {EXPECTED_COLUMNS}"
        )

    inserted = 0
    errors = 0
    for line_num, row in enumerate(reader, start=2):
        validated = validate_row(row, line_num)
        if validated is None:
            errors += 1
        else:
            db.insert_epidemiological(validated)
            inserted += 1

    logger.info(f"Importacion completada: {inserted} insertados, {errors} errores")
    return {"inserted": inserted, "errors": errors}


def import_csv_file(filepath: str, db: Optional[Database] = None) -> dict[str, int]:
    with open(filepath) as f:
        content = f.read()
    return import_csv_string(content, db)


def generate_sample_csv(output_path: str) -> None:
    rows = [
        {"date": "2024-06-01", "municipality": "San Luis Potosi",
         "disease": "dengue", "confirmed_cases": "12",
         "hospitalizations": "3", "deaths": "0"},
        {"date": "2024-06-01", "municipality": "Soledad de Graciano Sanchez",
         "disease": "covid", "confirmed_cases": "8",
         "hospitalizations": "1", "deaths": "0"},
        {"date": "2024-06-02", "municipality": "Ciudad Valles",
         "disease": "hantavirus", "confirmed_cases": "2",
         "hospitalizations": "1", "deaths": "0"},
        {"date": "2024-06-02", "municipality": "Matehuala",
         "disease": "dengue", "confirmed_cases": "5",
         "hospitalizations": "1", "deaths": "1"},
        {"date": "2024-06-03", "municipality": "Rioverde",
         "disease": "covid", "confirmed_cases": "15",
         "hospitalizations": "4", "deaths": "1"},
    ]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    logger.info(f"CSV de ejemplo generado en {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Importar datos epidemiologicos desde CSV"
    )
    parser.add_argument("file", nargs="?", help="Ruta al archivo CSV")
    parser.add_argument(
        "--generate-sample", action="store_true",
        help="Generar archivo CSV de ejemplo"
    )
    args = parser.parse_args()

    if args.generate_sample:
        output = "data/processed/sample_import.csv"
        generate_sample_csv(output)
        return

    if not args.file:
        parser.print_help()
        sys.exit(1)

    result = import_csv_file(args.file)
    print(f"Resultado: {result['inserted']} insertados, {result['errors']} errores")


if __name__ == "__main__":
    main()
