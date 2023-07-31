"""Configurations and mocks for testing."""

import pandas as pd
import pytest

from optitrader.enums import ObjectiveName
from optitrader.market import MarketData
from optitrader.market.investment_universe import UniverseName
from optitrader.models import ObjectiveModel, OptimizationRequest
from optitrader.optimization.objectives import ObjectiveValue
from optitrader.portfolio import Portfolio


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
def market_data_nodb() -> MarketData:
    """Mock MarketData instance without db."""
    return MarketData(use_db=False)


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
        universe_name=UniverseName.POPULAR_STOCKS,
        objectives=[ObjectiveModel(name=ObjectiveName.CVAR, weight=1)],
    )


@pytest.fixture()
def optimization_request_w_dates(
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> OptimizationRequest:
    """Mock optimization_request."""
    return OptimizationRequest(
        universe_name=UniverseName.POPULAR_STOCKS,
        objectives=[ObjectiveModel(name=ObjectiveName.CVAR, weight=1)],
        start_date=test_start_date,
        end_date=test_end_date,
    )


@pytest.fixture()
def mock_ptf() -> Portfolio:
    """Mock portfolio."""
    return Portfolio(
        weights=pd.Series(
            {
                "MSFT": 0.3,
                "TSLA": 0.2,
                "AAPL": 0.5,
            }
        ),
        objective_values=[ObjectiveValue(name=ObjectiveName.CVAR, value=0.1, weight=1.0)],
    )
