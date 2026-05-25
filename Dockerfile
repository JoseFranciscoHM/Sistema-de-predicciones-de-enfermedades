FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data models && \
    PYTHONPATH=src python -c "
from database import Database
from synthetic_data import generate_all_synthetic_data
db = Database('data/database.db')
generate_all_synthetic_data(db)
print('Datos sinteticos generados')
"

CMD PYTHONPATH=src python -m uvicorn app:app --host 0.0.0.0 --port $PORT
