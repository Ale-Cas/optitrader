"""Configurations and mocks for testing."""

import pandas as pd
import pytest

from optifolio.market import MarketData
from optifolio.market.investment_universe import InvestmentUniverse, UniverseName
from optifolio.models import ObjectiveModel, OptimizationRequest
from optifolio.optimization.objectives import ObjectiveName


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


@pytest.fixture()
def optimization_request() -> OptimizationRequest:
    """Mock optimization_request."""
    return OptimizationRequest(
        tickers=InvestmentUniverse(name=UniverseName.POPULAR_STOCKS).tickers,
        objectives=[ObjectiveModel(name=ObjectiveName.CVAR, weight=1)],
    )
