import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

DEFAULT_DB_PATH = str(Path(__file__).resolve().parent.parent / "data" / "database.db")


class Database:
    def __init__(self, db_path: str = DEFAULT_DB_PATH, auto_create: bool = True):
        self._db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        if auto_create:
            self.create_tables()

    def _connect(self) -> sqlite3.Connection:
        if self._conn is None:
            Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def _execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        return self._connect().execute(sql, params)

    def _fetchall(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        return self._execute(sql, params).fetchall()

    def _fetchone(self, sql: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        return self._execute(sql, params).fetchone()

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        return dict(row)

    def _rows_to_dicts(self, rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
        return [dict(r) for r in rows]

    def create_tables(self) -> None:
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS search_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                keyword VARCHAR(100) NOT NULL,
                value FLOAT NOT NULL,
                region VARCHAR(10) NOT NULL,
                disease VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS epidemiological_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                disease VARCHAR(50) NOT NULL,
                municipality VARCHAR(100) NOT NULL,
                confirmed_cases INTEGER NOT NULL DEFAULT 0,
                hospitalizations INTEGER NOT NULL DEFAULT 0,
                deaths INTEGER NOT NULL DEFAULT 0,
                source VARCHAR(50) NOT NULL DEFAULT 'api',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS clinical_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                disease VARCHAR(50) NOT NULL,
                municipality VARCHAR(100) NOT NULL,
                hantavirus_type VARCHAR(50),
                dengue_severity VARCHAR(20),
                symptoms TEXT,
                source VARCHAR(50) NOT NULL DEFAULT 'doctor',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                disease VARCHAR(50) NOT NULL,
                municipality VARCHAR(100) NOT NULL,
                outbreak_probability FLOAT NOT NULL,
                estimated_cases_7d FLOAT NOT NULL,
                ci_lower FLOAT,
                ci_upper FLOAT,
                model_version VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease VARCHAR(50) NOT NULL,
                sensitivity FLOAT,
                specificity FLOAT,
                rmse FLOAT,
                precision FLOAT,
                accuracy FLOAT,
                trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                training_duration_s FLOAT,
                num_epochs INTEGER
            )
        """
        )
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS keyword_overrides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease VARCHAR(50) NOT NULL,
                keyword VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(disease, keyword)
            )
        """
        )
        self._connect().commit()

    def get_table_names(self) -> set[str]:
        rows = self._fetchall(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return {r["name"] for r in rows}

    # --- Search Trends ---

    def insert_search_trend(self, entry: dict[str, Any]) -> None:
        self._execute(
            """
            INSERT INTO search_trends (date, keyword, value, region, disease)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                entry["date"],
                entry["keyword"],
                entry["value"],
                entry["region"],
                entry["disease"],
            ),
        )
        self._connect().commit()

    def get_search_trends(
        self, disease: str, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        rows = self._fetchall(
            """
            SELECT * FROM search_trends
            WHERE disease = ? AND date BETWEEN ? AND ?
            ORDER BY date
            """,
            (disease, start_date, end_date),
        )
        return self._rows_to_dicts(rows)

    # --- Epidemiological Data ---

    def insert_epidemiological(self, entry: dict[str, Any]) -> None:
        self._execute(
            """
            INSERT INTO epidemiological_data
                (date, disease, municipality, confirmed_cases, hospitalizations, deaths, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry["date"],
                entry["disease"],
                entry["municipality"],
                entry["confirmed_cases"],
                entry["hospitalizations"],
                entry["deaths"],
                entry.get("source", "api"),
            ),
        )
        self._connect().commit()

    def insert_clinical_data(self, entry: dict[str, Any]) -> None:
        self._execute(
            """
            INSERT INTO clinical_data
                (date, disease, municipality, hantavirus_type, dengue_severity, symptoms)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                entry["date"],
                entry["disease"],
                entry["municipality"],
                entry.get("hantavirus_type"),
                entry.get("dengue_severity"),
                entry.get("symptoms"),
            ),
        )
        self._connect().commit()

    def get_epidemiological(
        self,
        disease: str,
        start_date: date,
        end_date: date,
        municipality: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        if municipality:
            rows = self._fetchall(
                """
                SELECT * FROM epidemiological_data
                WHERE disease = ? AND date BETWEEN ? AND ? AND municipality = ?
                ORDER BY date
                """,
                (disease, start_date, end_date, municipality),
            )
        else:
            rows = self._fetchall(
                """
                SELECT * FROM epidemiological_data
                WHERE disease = ? AND date BETWEEN ? AND ?
                ORDER BY date
                """,
                (disease, start_date, end_date),
            )
        return self._rows_to_dicts(rows)

    def get_timeseries(
        self, disease: str, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        rows = self._fetchall(
            """
            SELECT date, SUM(confirmed_cases) as confirmed_cases,
                   SUM(hospitalizations) as hospitalizations,
                   SUM(deaths) as deaths
            FROM epidemiological_data
            WHERE disease = ? AND date BETWEEN ? AND ?
            GROUP BY date
            ORDER BY date
            """,
            (disease, start_date, end_date),
        )
        return self._rows_to_dicts(rows)

    def get_municipality_data(
        self, disease: str, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> list[dict[str, Any]]:
        if start_date and end_date:
            rows = self._fetchall(
                """
                SELECT municipality, SUM(confirmed_cases) as total_cases,
                       SUM(hospitalizations) as total_hosp,
                       SUM(deaths) as total_deaths
                FROM epidemiological_data
                WHERE disease = ? AND date BETWEEN ? AND ?
                GROUP BY municipality
                ORDER BY municipality
                """,
                (disease, start_date, end_date),
            )
        else:
            rows = self._fetchall(
                """
                SELECT municipality, SUM(confirmed_cases) as total_cases,
                       SUM(hospitalizations) as total_hosp,
                       SUM(deaths) as total_deaths
                FROM epidemiological_data
                WHERE disease = ?
                GROUP BY municipality
                ORDER BY municipality
                """,
                (disease,),
            )
        return self._rows_to_dicts(rows)

    # --- Predictions ---

    def insert_prediction(self, entry: dict[str, Any]) -> None:
        self._execute(
            """
            INSERT INTO predictions
                (date, disease, municipality, outbreak_probability,
                 estimated_cases_7d, ci_lower, ci_upper, model_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry["date"],
                entry["disease"],
                entry["municipality"],
                entry["outbreak_probability"],
                entry["estimated_cases_7d"],
                entry.get("ci_lower"),
                entry.get("ci_upper"),
                entry.get("model_version", "v1.0"),
            ),
        )
        self._connect().commit()

    def get_predictions(
        self, disease: str, municipality: Optional[str] = None
    ) -> list[dict[str, Any]]:
        if municipality:
            rows = self._fetchall(
                """
                SELECT * FROM predictions
                WHERE disease = ? AND municipality = ?
                ORDER BY date DESC
                """,
                (disease, municipality),
            )
        else:
            rows = self._fetchall(
                """
                SELECT * FROM predictions
                WHERE disease = ?
                ORDER BY date DESC
                """,
                (disease,),
            )
        return self._rows_to_dicts(rows)

    # --- Model Metrics ---

    def insert_model_metrics(self, entry: dict[str, Any]) -> None:
        self._execute(
            """
            INSERT INTO model_metrics
                (disease, sensitivity, specificity, rmse, precision, accuracy,
                 training_duration_s, num_epochs)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry["disease"],
                entry.get("sensitivity"),
                entry.get("specificity"),
                entry.get("rmse"),
                entry.get("precision"),
                entry.get("accuracy"),
                entry.get("training_duration_s"),
                entry.get("num_epochs"),
            ),
        )
        self._connect().commit()

    def get_latest_metrics(self, disease: str) -> Optional[dict[str, Any]]:
        row = self._fetchone(
            """
            SELECT * FROM model_metrics
            WHERE disease = ?
            ORDER BY trained_at DESC
            LIMIT 1
            """,
            (disease,),
        )
        return self._row_to_dict(row) if row else None

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    # --- Keyword Overrides ---

    def get_keyword_overrides(self, disease: str) -> list[str]:
        rows = self._fetchall(
            "SELECT keyword FROM keyword_overrides WHERE disease = ? ORDER BY keyword",
            (disease,),
        )
        return [r["keyword"] for r in rows]

    def add_keyword_override(self, disease: str, keyword: str) -> None:
        self._execute(
            "INSERT OR IGNORE INTO keyword_overrides (disease, keyword) VALUES (?, ?)",
            (disease, keyword.lower().strip()),
        )
        self._connect().commit()

    def remove_keyword_override(self, disease: str, keyword: str) -> None:
        self._execute(
            "DELETE FROM keyword_overrides WHERE disease = ? AND keyword = ?",
            (disease, keyword.lower().strip()),
        )
        self._connect().commit()

    def get_all_keywords(self, disease: str) -> list[str]:
        from synthetic_data import KEYWORDS
        base = KEYWORDS.get(disease, [])
        overrides = self.get_keyword_overrides(disease)
        merged = list(base)
        for kw in overrides:
            if kw not in merged:
                merged.append(kw)
        return merged
