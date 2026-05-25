#!/bin/bash
set -e

echo "=== Inicializando base de datos ==="
cd /app

mkdir -p data models

if [ ! -f data/database.db ]; then
    echo "Generando datos sinteticos..."
    PYTHONPATH=src python -c "
from database import Database
from synthetic_data import generate_all_synthetic_data
db = Database('data/database.db')
generate_all_synthetic_data(db)
print('Datos sinteticos generados exitosamente')
"
fi

echo "=== Iniciando servidor ==="
exec PYTHONPATH=src python -m uvicorn app:app --host 0.0.0.0 --port "$PORT"
