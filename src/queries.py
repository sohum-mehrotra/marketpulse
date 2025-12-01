from typing import Optional

import pandas as pd

from .db import q


def get_companies(limit: int = 50, sector: Optional[str] = None) -> pd.DataFrame:
    sql = """
    SELECT Symbol, Shortname, Sector, Industry,
           Currentprice, Marketcap, Weight
    FROM companies
    """
    params: dict = {}

    if sector:
        sql += " WHERE Sector = :sector"
        params["sector"] = sector

    sql += " ORDER BY Marketcap DESC"

    if limit:
        sql += " LIMIT :limit"
        params["limit"] = limit

    return q(sql, params)


def get_company(symbol: str) -> pd.DataFrame:
    sql = """
    SELECT *
    FROM companies
    WHERE Symbol = :symbol
    """
    return q(sql, {"symbol": symbol})


def get_sectors() -> pd.DataFrame:
    sql = """
    SELECT DISTINCT Sector
    FROM companies
    ORDER BY Sector
    """
    return q(sql)


def get_sector_companies_with_stats(sector: str | None = None) -> pd.DataFrame:
    """
    INNER JOIN between companies and sector_stats to show per-company info
    plus aggregated sector metrics.
    """
    sql = """
    SELECT
        c.Symbol,
        c.Shortname,
        c.Sector,
        c.Industry,
        c.Currentprice,
        c.Marketcap,
        s.n_companies,
        s.avg_marketcap,
        s.total_weight
    FROM companies AS c
    INNER JOIN sector_stats AS s
        ON c.Sector = s.Sector
    """
    params: dict = {}

    if sector:
        sql += " WHERE c.Sector = :sector"
        params["sector"] = sector

    sql += """
    ORDER BY s.total_weight DESC, c.Marketcap DESC
    """

    return q(sql, params)


def get_index_history(limit: int = 100) -> pd.DataFrame:
    sql = """
    SELECT Date, [S&P500] AS sp500
    FROM index_history
    ORDER BY Date DESC
    LIMIT :limit
    """
    return q(sql, {"limit": limit})

