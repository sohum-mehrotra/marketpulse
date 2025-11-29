import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path("/tmp/marketpulse.db")

# Use env var if provided (for flexibility), else local SQLite file
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

_engine: Engine | None = None


def get_engine() -> Engine:
    """Singleton SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, echo=False, future=True)
    return _engine


def q(sql: str, params: dict | None = None) -> pd.DataFrame:
    """
    Run a SELECT query and return a pandas DataFrame.
    Mirrors the q() helper from Case Study 06. :contentReference[oaicite:0]{index=0}
    """
    engine = get_engine()
    return pd.read_sql(text(sql), engine, params=params)


def exec_sql(sql: str, params: dict | None = None) -> None:
    """
    Run DDL/INSERT/UPDATE/DELETE with no return value.
    Mirrors exec_sql() pattern from Case Study 06. :contentReference[oaicite:1]{index=1}
    """
    engine = get_engine()
    with engine.begin() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys = ON;")
        conn.execute(text(sql), params or {})


def init_db(rebuild: bool = False) -> None:
    """
    Create/populate SQLite DB from the two CSVs and a derived sector_stats table.
    Safe to call multiple times.
    """
    if rebuild and DB_PATH.exists() and DATABASE_URL.startswith("sqlite"):
        DB_PATH.unlink()

    engine = get_engine()

    # Load CSVs into DataFrames
    companies_csv = BASE_DIR / "assets" / "sp500_companies.csv"
    index_csv = BASE_DIR / "assets" / "sp500_index.csv"

    companies = pd.read_csv(companies_csv)
    index_history = pd.read_csv(index_csv)

    # Normalize column names for SQL friendliness
    companies.columns = [c.replace(" ", "_") for c in companies.columns]
    index_history.columns = [
        c.replace(" ", "_").replace("&", "and") for c in index_history.columns
    ]

    # Persist tables
    companies.to_sql("companies", engine, if_exists="replace", index=False)
    index_history.to_sql("index_history", engine, if_exists="replace", index=False)

    # Derived table: sector-level stats (shows GROUP BY + JOIN concept)
    sector_stats = (
        companies.groupby("Sector")
        .agg(
            n_companies=("Symbol", "nunique"),
            avg_marketcap=("Marketcap", "mean"),
            total_weight=("Weight", "sum"),
        )
        .reset_index()
    )
    sector_stats.to_sql("sector_stats", engine, if_exists="replace", index=False)
