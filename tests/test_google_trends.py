from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from data_sources.google_trends import GoogleTrendsClient


def test_fetch_keyword_empty_on_response_error():
    client = GoogleTrendsClient()
    with patch.object(
        client, "_get_client"
    ) as mock_get_client:
        mock_client = MagicMock()
        mock_client.build_payload.side_effect = Exception("API error")
        mock_get_client.return_value = mock_client

        results = client.fetch_keyword("tos", region="MX")
        assert results == []


def test_fetch_keyword_empty_dataframe():
    client = GoogleTrendsClient()
    with patch.object(
        client, "_get_client"
    ) as mock_get_client:
        mock_client = MagicMock()
        mock_client.build_payload.return_value = None
        mock_client.interest_over_time.return_value = pd.DataFrame()
        mock_get_client.return_value = mock_client

        results = client.fetch_keyword("fiebre", region="SLP")
        assert results == []


def test_fetch_disease_unknown():
    client = GoogleTrendsClient()
    results = client.fetch_disease_trends("unknown_disease")
    assert results == []


def test_fetch_all_diseases_empty():
    client = GoogleTrendsClient()
    with patch.object(
        client, "_get_client"
    ) as mock_get_client:
        mock_client = MagicMock()
        mock_client.build_payload.return_value = None
        mock_client.interest_over_time.return_value = pd.DataFrame()
        mock_get_client.return_value = mock_client

        results = client.fetch_all_diseases()
        assert results == []
