"""Test market_data module."""
import pandas as pd
import pytest
import vcr

from optifolio.market import MarketData
from optifolio.models.asset import AssetModel


@pytest.mark.vcr()
def test_load_prices(
    market_data: MarketData,
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test load_prices method."""
    prices = market_data.load_prices(
        tickers=test_tickers,
        start_date=test_start_date,
        end_date=test_end_date,
    )
    assert isinstance(prices, pd.DataFrame)
    assert sorted(prices.columns) == sorted(test_tickers)


@vcr.use_cassette("tests/data/cassettes/test_load_prices.yaml")
def test_get_total_returns(
    market_data: MarketData,
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test get_total_returns method."""
    returns = market_data.get_total_returns(
        tickers=test_tickers,
        start_date=test_start_date,
        end_date=test_end_date,
    )
    assert isinstance(returns, pd.DataFrame)
    assert sorted(returns.columns) == sorted(test_tickers)


def test_get_asset(
    market_data: MarketData,
) -> None:
    """Test get_total_returns method."""
    asset = market_data.get_asset_from_ticker(
        ticker="AAPL",
    )
    assert isinstance(asset, AssetModel)
