"""Test yahoo query integration."""

from pandas import DataFrame, Series

from optifolio.market.yahoo_market_data import YahooMarketData
from optifolio.models.asset import YahooAssetModel

client = YahooMarketData()


def test_get_yahoo_asset() -> None:
    """Test get_yahoo_asset method."""
    asset = client.get_yahoo_asset(ticker="AAPL")
    assert isinstance(asset, YahooAssetModel)


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
