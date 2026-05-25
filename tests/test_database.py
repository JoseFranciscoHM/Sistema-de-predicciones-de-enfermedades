import pytest
from datetime import date, datetime
from database import Database


@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    db.create_tables()
    return db


def test_create_tables(db):
    tables = db.get_table_names()
    expected = {
        "search_trends",
        "epidemiological_data",
        "clinical_data",
        "predictions",
        "model_metrics",
    }
    assert expected.issubset(tables)


def test_insert_and_get_search_trends(db):
    entry = {
        "date": date(2024, 6, 1),
        "keyword": "tos",
        "value": 75.0,
        "region": "SLP",
        "disease": "hantavirus",
    }
    db.insert_search_trend(entry)
    results = db.get_search_trends("hantavirus", date(2024, 5, 1), date(2024, 7, 1))
    assert len(results) == 1
    assert results[0]["keyword"] == "tos"
    assert results[0]["value"] == 75.0


def test_insert_and_get_epidemiological(db):
    entry = {
        "date": date(2024, 6, 1),
        "disease": "dengue",
        "municipality": "San Luis Potosi",
        "confirmed_cases": 10,
        "hospitalizations": 2,
        "deaths": 0,
        "source": "sintetico",
    }
    db.insert_epidemiological(entry)
    results = db.get_epidemiological(
        "dengue", date(2024, 5, 1), date(2024, 7, 1), "San Luis Potosi"
    )
    assert len(results) == 1
    assert results[0]["confirmed_cases"] == 10


def test_insert_and_get_predictions(db):
    entry = {
        "date": date(2024, 6, 10),
        "disease": "covid",
        "municipality": "Soledad",
        "outbreak_probability": 0.35,
        "estimated_cases_7d": 15.0,
        "ci_lower": 8.0,
        "ci_upper": 22.0,
        "model_version": "v1.0",
    }
    db.insert_prediction(entry)
    results = db.get_predictions("covid", "Soledad")
    assert len(results) >= 1
    assert results[0]["outbreak_probability"] == 0.35


def test_insert_and_get_model_metrics(db):
    entry = {
        "disease": "hantavirus",
        "sensitivity": 0.82,
        "specificity": 0.79,
        "rmse": 5.3,
        "precision": 0.80,
        "accuracy": 0.81,
        "training_duration_s": 120.5,
        "num_epochs": 50,
    }
    db.insert_model_metrics(entry)
    latest = db.get_latest_metrics("hantavirus")
    assert latest is not None
    assert latest["sensitivity"] == 0.82


def test_get_timeseries(db):
    for i in range(5):
        db.insert_epidemiological(
            {
                "date": date(2024, 6, 1 + i),
                "disease": "dengue",
                "municipality": "Capital",
                "confirmed_cases": 5 + i,
                "hospitalizations": 1,
                "deaths": 0,
                "source": "sintetico",
            }
        )
    ts = db.get_timeseries("dengue", date(2024, 6, 1), date(2024, 6, 10))
    assert len(ts) == 5
    assert ts[0]["confirmed_cases"] == 5
    assert ts[-1]["confirmed_cases"] == 9


def test_get_municipality_data(db):
    for mun in ["A", "B"]:
        db.insert_epidemiological(
            {
                "date": date(2024, 6, 1),
                "disease": "dengue",
                "municipality": mun,
                "confirmed_cases": 10,
                "hospitalizations": 2,
                "deaths": 0,
                "source": "sintetico",
            }
        )
    data = db.get_municipality_data("dengue")
    assert len(data) == 2
    municipalities = {r["municipality"] for r in data}
    assert municipalities == {"A", "B"}
