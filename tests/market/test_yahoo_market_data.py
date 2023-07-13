"""Test yahoo query integration."""

import pytest
from pandas import DataFrame, Series, Timestamp

from optifolio.market.yahoo_market_data import YahooMarketData
from optifolio.models.asset import YahooAssetModel

client = YahooMarketData()


def test_get_yahoo_asset() -> None:
    """Test get_yahoo_asset method."""
    asset = client.get_yahoo_asset(ticker="AAPL")
    assert isinstance(asset, YahooAssetModel)


def test_get_yahoo_asset_failure() -> None:
    """Test get_yahoo_asset method."""
    with pytest.raises(AssertionError, match="Yahoo query"):
        client.get_yahoo_asset(ticker="INVLIDTICKER", fail_on_yf_error=True)


def test_get_yahoo_invalid_asset() -> None:
    """Test get_yahoo_asset method."""
    asset = client.get_yahoo_asset(ticker="INVALIDTICKER")
    assert isinstance(asset, YahooAssetModel)


def test_get_bars(test_start_date: Timestamp) -> None:
    """Test get_bars method."""
    bars = client.get_bars(tickers=("AAPL",), start_date=test_start_date)
    assert isinstance(bars, DataFrame)


def test_get_prices(test_start_date: Timestamp) -> None:
    """Test get_prices method."""
    prices = client.get_prices(tickers=("AAPL", "TSLA", "BRK.B"), start_date=test_start_date)
    assert isinstance(prices, DataFrame)


def test_get_yahoo_number_of_shares() -> None:
    """Test get_yahoo_asset method."""
    shares = client.get_number_of_shares(ticker="AAPL")
    assert isinstance(shares, int)


def test_get_multi_number_of_shares() -> None:
    """Test get_yahoo_asset method."""
    test_tickers = ("AAPL", "MSFT", "BRK.B")
    shares = client.get_multi_number_of_shares(test_tickers)
    assert isinstance(shares, Series)
    assert sorted(shares.index) == sorted(test_tickers)


def test_get_financials() -> None:
    """Test get_financials method."""
    fin_df = client.get_financials(ticker="AAPL")
    assert isinstance(fin_df, DataFrame)
    assert all(fin_df.columns == client.financials)


def test_get_multi_financials_by_item(test_tickers: tuple[str, ...]) -> None:
    """Test get_multi_financials_by_item method."""
    fin_df = client.get_multi_financials_by_item(tickers=test_tickers)
    assert isinstance(fin_df, DataFrame)
    assert sorted(fin_df.columns) == sorted(test_tickers)
