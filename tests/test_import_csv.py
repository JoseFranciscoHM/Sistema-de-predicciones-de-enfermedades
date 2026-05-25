import csv
import io
from datetime import date

import pytest

from database import Database


CSV_HEADER = [
    "date", "municipality", "disease",
    "confirmed_cases", "hospitalizations", "deaths",
]


def _make_csv(rows: list[dict]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_HEADER)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    db.create_tables()
    return db


def test_import_valid_csv(db, monkeypatch):
    from import_csv import import_csv_string

    csv_data = _make_csv([
        {
            "date": "2024-06-01",
            "municipality": "San Luis Potosi",
            "disease": "dengue",
            "confirmed_cases": "10",
            "hospitalizations": "2",
            "deaths": "0",
        },
    ])
    result = import_csv_string(csv_data, db)
    assert result["inserted"] == 1
    assert result["errors"] == 0


def test_import_invalid_date_format(db, monkeypatch):
    from import_csv import import_csv_string

    csv_data = _make_csv([
        {
            "date": "invalid-date",
            "municipality": "San Luis Potosi",
            "disease": "dengue",
            "confirmed_cases": "10",
            "hospitalizations": "2",
            "deaths": "0",
        },
    ])
    result = import_csv_string(csv_data, db)
    assert result["inserted"] == 0
    assert result["errors"] == 1


def test_import_negative_cases(db, monkeypatch):
    from import_csv import import_csv_string

    csv_data = _make_csv([
        {
            "date": "2024-06-01",
            "municipality": "San Luis Potosi",
            "disease": "dengue",
            "confirmed_cases": "-5",
            "hospitalizations": "2",
            "deaths": "0",
        },
    ])
    result = import_csv_string(csv_data, db)
    assert result["inserted"] == 0
    assert result["errors"] == 1


def test_import_partial_valid(db, monkeypatch):
    from import_csv import import_csv_string

    csv_data = _make_csv([
        {
            "date": "2024-06-01",
            "municipality": "San Luis Potosi",
            "disease": "dengue",
            "confirmed_cases": "10",
            "hospitalizations": "2",
            "deaths": "0",
        },
        {
            "date": "bad-date",
            "municipality": "Soledad",
            "disease": "covid",
            "confirmed_cases": "5",
            "hospitalizations": "1",
            "deaths": "0",
        },
    ])
    result = import_csv_string(csv_data, db)
    assert result["inserted"] == 1
    assert result["errors"] == 1


def test_sample_csv_generated(db, monkeypatch, tmp_path):
    from import_csv import generate_sample_csv

    csv_path = tmp_path / "sample.csv"
    generate_sample_csv(str(csv_path))
    assert csv_path.exists()

    with open(csv_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) >= 3
    assert rows[0]["disease"] in ("hantavirus", "covid", "dengue")
