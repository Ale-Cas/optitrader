"""Configurations and mocks for testing."""
import pandas as pd
import pytest

from optifolio.market import MarketData


@pytest.fixture(scope="package")
def vcr_config(record_mode: str = "once"):
    """Cassettes config.

    Params
    ------
    record_mode:
        - "rewrite": rewrite all cassettes if they have changed.
        - "none": only replay cassettes or throw an error if they are missing.
        - "once": record if there is no cassette, and if there is one replay it.
    """
    return {
        "record_mode": record_mode,
        "filter_headers": [
            ("APCA-API-KEY-ID", "SECRET"),
            ("APCA-API-SECRET-KEY", "SECRET"),
        ],
    }


@pytest.fixture()
def market_data() -> MarketData:
    """Mock MarketData instance."""
    return MarketData()


@pytest.fixture()
def test_tickers() -> tuple[str, ...]:
    """Mock tickers for tests."""
    return (
        "AAPL",
        "TSLA",
        "MSFT",
        "V",
        "JPM",
    )


@pytest.fixture()
def test_start_date() -> pd.Timestamp:
    """Start date for testing."""
    return pd.Timestamp("2023-01-01").normalize()


@pytest.fixture()
def test_end_date() -> pd.Timestamp:
    """Start date for testing."""
    return pd.Timestamp("2023-06-01").normalize()
