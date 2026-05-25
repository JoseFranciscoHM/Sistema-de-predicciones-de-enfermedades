from datetime import date
from unittest.mock import patch

from data_sources.government_apis import (
    fetch_from_datos_mexico,
    fetch_from_sinais,
    fetch_from_all_sources,
)


def test_datos_mexico_fallback_on_timeout():
    with patch("data_sources.government_apis.requests.get") as mock_get:
        mock_get.side_effect = Exception("Timeout")
        results = fetch_from_datos_mexico(
            "covid", date(2024, 1, 1), date(2024, 1, 31)
        )
        assert results == []


def test_sinais_fallback_on_error():
    with patch("data_sources.government_apis.requests.get") as mock_get:
        mock_get.side_effect = Exception("Connection error")
        results = fetch_from_sinais(
            "dengue", date(2024, 6, 1), date(2024, 6, 30)
        )
        assert results == []


def test_fetch_from_all_sources_all_fail():
    with patch(
        "data_sources.government_apis.fetch_from_datos_mexico",
        return_value=[],
    ), patch(
        "data_sources.government_apis.fetch_from_sinais",
        return_value=[],
    ):
        results = fetch_from_all_sources(
            "hantavirus", date(2024, 1, 1), date(2024, 12, 31)
        )
        assert results == []
