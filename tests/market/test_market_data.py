"""Test market_data module."""
import pandas as pd
import pytest
import vcr

from optifolio.enums import UniverseName
from optifolio.market import InvestmentUniverse, MarketData
from optifolio.models import AssetModel


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


def test_get_market_caps(
    market_data: MarketData,
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test get_market_caps method."""
    mkt_caps = market_data.get_market_caps(
        tickers=test_tickers,
        start_date=test_start_date,
        end_date=test_end_date,
    )
    assert isinstance(mkt_caps, pd.DataFrame)
    assert sorted(mkt_caps.columns) == sorted(test_tickers)


@pytest.mark.vcr()
def test_get_asset(
    market_data: MarketData,
) -> None:
    """Test get_total_returns method."""
    asset = market_data.get_asset_from_ticker(
        ticker="AAPL",
    )
    assert isinstance(asset, AssetModel)


def test_investment_universe_with_top_market_cap(
    market_data: MarketData,
) -> None:
    """Test the investment universe initialization with the top_market_cap."""
    _top = 2

    tickers = market_data.get_top_market_cap_tickers(
        top=_top, tickers=InvestmentUniverse(name=UniverseName.FAANG).tickers
    )
    assert len(tickers) == _top
