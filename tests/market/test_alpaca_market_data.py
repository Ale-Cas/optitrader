"""Test market_data module."""
import pandas as pd
import pytest
import vcr

from optifolio.market.alpaca_market_data import AlpacaMarketData, Asset

alpaca_market_data = AlpacaMarketData()


@pytest.mark.vcr()
def test_get_bars(
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test load_prices method."""
    bars = alpaca_market_data.get_bars(
        tickers=test_tickers,
        start_date=test_start_date,
        end_date=test_end_date,
    )
    assert isinstance(bars, pd.DataFrame)


@pytest.mark.vcr()
def test_get_assets_df() -> None:
    """Test load_prices method."""
    assets_df = alpaca_market_data.get_assets_df()
    assert isinstance(assets_df, pd.DataFrame)


@vcr.use_cassette("tests/cassettes/test_get_assets_df.yaml")
def test_get_asset_by_name() -> None:
    """Test load_prices method."""
    asset = alpaca_market_data.get_asset_by_name("Apple")
    assert isinstance(asset, Asset)


@vcr.use_cassette("tests/cassettes/test_get_bars.yaml")
def test_get_prices(
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test get_total_returns method."""
    prices = alpaca_market_data.get_prices(
        tickers=test_tickers,
        start_date=test_start_date,
        end_date=test_end_date,
    )
    assert isinstance(prices, pd.DataFrame)
    assert sorted(prices.columns) == sorted(test_tickers)
