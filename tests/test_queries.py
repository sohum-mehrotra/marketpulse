import os
os.environ["DATABASE_URL"] = "sqlite:////tmp/marketpulse_test.db"

from src.db import init_db
from src import queries


def setup_module(module):
    init_db(rebuild=True)


def test_get_companies_not_empty():
    df = queries.get_companies(limit=5)
    assert not df.empty
    assert "Symbol" in df.columns


def test_get_sectors_not_empty():
    df = queries.get_sectors()
    assert not df.empty
    assert "Sector" in df.columns
