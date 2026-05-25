import csv
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np

random.seed(42)
np.random.seed(42)

DISEASES = ["hantavirus", "covid", "dengue"]

KEYWORDS: dict[str, list[str]] = {
    "hantavirus": [
        "tos", "fiebre", "dolor muscular", "dificultad para respirar",
        "sangrado", "raton de campo", "hantavirus sintomas",
    ],
    "covid": [
        "covid tos", "covid fiebre", "perdida de olfato",
        "covid mexico", "covid slp",
    ],
    "dengue": [
        "dengue fiebre", "dolor de huesos", "sarpullido",
        "dengue slp", "mosquito",
    ],
}

MUNICIPALITIES: list[str] = [
    "Ahualulco", "Alaquines", "Aquismon", "Armadillo de los Infante",
    "Axtla de Terrazas", "Cardenas", "Catorce", "Cedral", "Cerritos",
    "Cerro de San Pedro", "Charcas", "Ciudad del Maiz", "Ciudad Fernandez",
    "Ciudad Valles", "Coxcatlan", "Ebano", "El Naranjo", "Guadalcazar",
    "Huehuetlan", "Lagunillas", "Matehuala", "Matlapa",
    "Mexquitic de Carmona", "Moctezuma", "Rayon", "Rioverde", "Salinas",
    "San Antonio", "San Ciro de Acosta", "San Luis Potosi",
    "San Martin Chalchicuautla", "San Nicolas Tolentino",
    "San Vicente Tancuayalab", "Santa Catarina", "Santa Maria del Rio",
    "Santo Domingo", "Soledad de Graciano Sanchez", "Tamasopo",
    "Tamazunchale", "Tampacan", "Tampamolon Corona", "Tamuin",
    "Tancanhuitz", "Tanlajas", "Tanquian de Escobedo", "Tierra Nueva",
    "Vanegas", "Venado", "Villa de Arista", "Villa de Arriaga",
    "Villa de Guadalupe", "Villa de la Paz", "Villa de Ramos",
    "Villa de Reyes", "Villa Hidalgo", "Villa Juarez", "Xilitla",
    "Zaragoza",
]

POPULATION_WEIGHTS: dict[str, float] = {
    "San Luis Potosi": 0.18,
    "Soledad de Graciano Sanchez": 0.08,
    "Ciudad Valles": 0.04,
    "Matehuala": 0.03,
    "Rioverde": 0.03,
    "Tamazunchale": 0.03,
    "Ebano": 0.02,
    "Tamuin": 0.02,
    "Aquismon": 0.02,
    "Xilitla": 0.02,
    "Tamasopo": 0.015,
    "Cardenas": 0.015,
    "Cedral": 0.015,
    "Salinas": 0.015,
    "Villa de Reyes": 0.015,
    "Villa de Arista": 0.015,
    "Villa de Arriaga": 0.015,
    "Ciudad del Maiz": 0.015,
    "Ciudad Fernandez": 0.015,
    "Cerritos": 0.015,
}

BASE_WEIGHT = 0.01


def get_municipality_population_weight(municipality: str) -> float:
    return POPULATION_WEIGHTS.get(municipality, BASE_WEIGHT)


def _normalize_weights() -> list[tuple[str, float]]:
    total = sum(get_municipality_population_weight(m) for m in MUNICIPALITIES)
    return [(m, get_municipality_population_weight(m) / total) for m in MUNICIPALITIES]


MUNICIPALITY_WEIGHTS = _normalize_weights()


def _seasonal_factor(d: date, disease: str) -> float:
    month = d.month
    day_of_year = d.timetuple().tm_yday

    if disease == "dengue":
        peak = 7
        width = 3
        factor = np.exp(-0.5 * ((month - peak) / width) ** 2)
        return float(factor * 2.0 + 0.3)
    elif disease == "covid":
        peak = 1
        width = 2.5
        m = month + 3
        if m > 12:
            m -= 12
        factor = np.exp(-0.5 * ((m - (peak + 3)) / width) ** 2)
        return float(factor * 1.8 + 0.2)
    elif disease == "hantavirus":
        return float(0.8 + 0.4 * np.sin(2 * np.pi * day_of_year / 365 - 1))
    return 1.0


def _trend_value(d: date, disease: str, keyword_index: int) -> float:
    base = 30.0 + 20.0 * _seasonal_factor(d, disease)
    noise = np.random.normal(0, 5)
    kw_offset = 10 * np.sin(keyword_index + 1)
    return max(0, min(100, base + kw_offset + noise))


def _cases(
    d: date, disease: str, population_weight: float
) -> tuple[int, int, int]:
    seasonal = _seasonal_factor(d, disease)
    base_cases = seasonal * population_weight * 50.0
    noise = np.random.poisson(max(1, base_cases * 0.3))
    confirmed = max(0, int(base_cases + noise))

    hosp_rate = random.uniform(0.05, 0.15)
    death_rate = random.uniform(0.01, 0.05) if disease != "covid" else random.uniform(0.005, 0.02)

    hospitalizations = int(confirmed * hosp_rate)
    deaths = int(confirmed * death_rate)

    return confirmed, hospitalizations, deaths


def generate_synthetic_data(
    start_date: date = date(2024, 1, 1),
    end_date: date = date(2026, 5, 24),
    num_municipalities: int | None = None,
) -> dict[str, list[dict[str, Any]]]:
    trends: list[dict[str, Any]] = []
    epidemiological: list[dict[str, Any]] = []

    municipalities = MUNICIPALITIES[:num_municipalities] if num_municipalities else MUNICIPALITIES
    current = start_date
    while current <= end_date:
        for disease in DISEASES:
            for ki, keyword in enumerate(KEYWORDS[disease]):
                for region in ["MX", "SLP"]:
                    trends.append({
                        "date": current,
                        "keyword": keyword,
                        "value": round(_trend_value(current, disease, ki), 2),
                        "region": region,
                        "disease": disease,
                    })

            for municipality in municipalities:
                pop_w = get_municipality_population_weight(municipality)
                conf, hosp, deaths = _cases(current, disease, pop_w)
                epidemiological.append({
                    "date": current,
                    "disease": disease,
                    "municipality": municipality,
                    "confirmed_cases": conf,
                    "hospitalizations": hosp,
                    "deaths": deaths,
                    "source": "sintetico",
                })
        current += timedelta(days=1)

    return {"trends": trends, "epidemiological": epidemiological}


def save_to_csv(data: dict[str, list[dict[str, Any]]], output_dir: str) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    trends_path = out / "search_trends.csv"
    with open(trends_path, "w", newline="") as f:
        if data["trends"]:
            w = csv.DictWriter(f, fieldnames=data["trends"][0].keys())
            w.writeheader()
            w.writerows(data["trends"])

    epi_path = out / "epidemiological_data.csv"
    with open(epi_path, "w", newline="") as f:
        if data["epidemiological"]:
            w = csv.DictWriter(f, fieldnames=data["epidemiological"][0].keys())
            w.writeheader()
            w.writerows(data["epidemiological"])

    print(f"Datos guardados en {out}")
    print(f"  Trends: {trends_path} ({len(data['trends'])} registros)")
    print(f"  Epidemiologicos: {epi_path} ({len(data['epidemiological'])} registros)")


if __name__ == "__main__":
    data = generate_synthetic_data()
    output_dir = str(Path(__file__).resolve().parent.parent / "data" / "synthetic_data")
    save_to_csv(data, output_dir)
