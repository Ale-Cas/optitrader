"""Test market_data module."""
import pandas as pd
import pytest
import vcr

from optifolio.market.alpaca_market_data import AlpacaMarketData


@pytest.mark.vcr()
def test_get_bars(
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test load_prices method."""
    bars = AlpacaMarketData().get_bars(
        tickers=test_tickers,
        start_date=test_start_date,
        end_date=test_end_date,
    )
    assert isinstance(bars, pd.DataFrame)


@vcr.use_cassette("tests/cassettes/test_get_bars.yaml")
def test_get_prices(
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test get_total_returns method."""
    prices = AlpacaMarketData().get_prices(
        tickers=test_tickers,
        start_date=test_start_date,
        end_date=test_end_date,
    )
    assert isinstance(prices, pd.DataFrame)
    assert sorted(prices.columns) == sorted(test_tickers)
