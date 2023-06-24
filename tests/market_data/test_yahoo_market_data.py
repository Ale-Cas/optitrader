"""Test yahoo query integration."""

from optifolio.market.yahoo_market_data import YahooMarketData
from optifolio.models.asset import YahooAssetModel


def test_get_yahoo_asset() -> None:
    """Test get_yahoo_asset method."""
    asset = YahooMarketData().get_yahoo_asset(ticker="AAPL")
    assert isinstance(asset, YahooAssetModel)
