import logging
from datetime import date, timedelta
from typing import Optional

from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError

from synthetic_data import DISEASES, KEYWORDS

logger = logging.getLogger(__name__)


class GoogleTrendsClient:
    def __init__(self, hl: str = "es-MX", tz: int = 180):
        self._pytrends: Optional[TrendReq] = None
        self._hl = hl
        self._tz = tz

    def _get_client(self) -> TrendReq:
        if self._pytrends is None:
            self._pytrends = TrendReq(hl=self._hl, tz=self._tz)
        return self._pytrends

    def fetch_keyword(
        self, keyword: str, region: str = "MX", timeframe: str = "today 3-m"
    ) -> list[dict]:
        try:
            client = self._get_client()
            geo = region if region == "MX" else "MX-SLP"
            client.build_payload(
                kw_list=[keyword],
                timeframe=timeframe,
                geo=geo,
                gprop="",
            )
            data = client.interest_over_time()
            if data.empty:
                logger.warning(f"Sin datos para keyword='{keyword}', region={region}")
                return []

            results = []
            for timestamp, row in data.iterrows():
                results.append({
                    "date": timestamp.date(),
                    "keyword": keyword,
                    "value": float(row[keyword]),
                    "region": region,
                })
            return results
        except ResponseError as e:
            logger.error(f"Error pytrends para keyword='{keyword}': {e}")
            return []
        except Exception as e:
            logger.exception(f"Error inesperado en pytrends: {e}")
            return []

    def fetch_disease_trends(
        self,
        disease: str,
        days_back: int = 90,
    ) -> list[dict]:
        if disease not in DISEASES:
            logger.warning(f"Enfermedad desconocida: {disease}")
            return []

        keywords = KEYWORDS[disease]
        results = []
        for keyword in keywords:
            for region in ["MX", "SLP"]:
                kw_results = self.fetch_keyword(keyword, region=region)
                for r in kw_results:
                    r["disease"] = disease
                results.extend(kw_results)

        return results

    def fetch_all_diseases(self, days_back: int = 90) -> list[dict]:
        all_results = []
        for disease in DISEASES:
            results = self.fetch_disease_trends(disease, days_back)
            all_results.extend(results)
            logger.info(
                f"{disease}: {len(results)} registros de tendencias obtenidos"
            )
        return all_results
