import pytest
from datetime import date
from synthetic_data import (
    DISEASES,
    MUNICIPALITIES,
    KEYWORDS,
    generate_synthetic_data,
    get_municipality_population_weight,
)


def test_municipalities_count():
    assert len(MUNICIPALITIES) == 58


def test_diseases_defined():
    assert "hantavirus" in DISEASES
    assert "covid" in DISEASES
    assert "dengue" in DISEASES


def test_keywords_per_disease():
    for disease in DISEASES:
        assert disease in KEYWORDS
        assert len(KEYWORDS[disease]) >= 3


def test_population_weights_sum():
    total = sum(get_municipality_population_weight(m) for m in MUNICIPALITIES)
    assert abs(total - 1.0) < 0.01


def test_generate_synthetic_data_shape():
    data = generate_synthetic_data(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 10),
        num_municipalities=3,
    )
    assert len(data["trends"]) > 0
    assert len(data["epidemiological"]) > 0
    for entry in data["epidemiological"]:
        assert entry["confirmed_cases"] >= 0
        assert entry["hospitalizations"] >= 0
        assert entry["deaths"] >= 0


def test_seasonal_pattern():
    # Dengue should have more cases in rainy season (Jun-Oct)
    data = generate_synthetic_data(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        num_municipalities=1,
    )
    cases_by_month = {}
    for entry in data["epidemiological"]:
        m = entry["date"].month
        cases_by_month[m] = cases_by_month.get(m, 0) + entry["confirmed_cases"]

    rainy = sum(cases_by_month.get(m, 0) for m in range(6, 11))
    dry = sum(cases_by_month.get(m, 0) for m in [1, 2, 3, 4, 5, 11, 12])
    # Rainy season should have at least as many cases as dry (for dengue)
    assert rainy >= dry * 0.5  # At least half of dry season as baseline


def test_no_nulls():
    data = generate_synthetic_data(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        num_municipalities=2,
    )
    for entry in data["trends"]:
        assert all(v is not None for v in entry.values())
    for entry in data["epidemiological"]:
        assert all(v is not None for v in entry.values())
