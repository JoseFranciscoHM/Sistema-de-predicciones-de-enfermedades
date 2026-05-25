#!/usr/bin/env bash
set -euo pipefail

echo "=== Seed All: Generando datos sintéticos y entrenando modelos ==="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${PYTHONPATH:-}:${SCRIPT_DIR}/src"

echo "[1/3] Generando datos sintéticos..."
python -m src.synthetic_data

echo "[2/3] Poblando base de datos..."
python -c "
from src.database import Database
db = Database()
db.create_tables()
print('Tablas creadas correctamente.')
"

echo "[3/3] Entrenando modelos RNN..."
python -m src.train_model --disease hantavirus
python -m src.train_model --disease covid
python -m src.train_model --disease dengue

echo "=== Done ==="
