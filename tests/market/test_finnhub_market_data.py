"""Test finnhub_market_data module."""
import time
from unittest.mock import Mock

import finnhub
import pandas as pd
import pytest
import vcr

from optifolio.enums.market import UniverseName
from optifolio.market.finnhub_market_data import FinnhubClient
from optifolio.market.investment_universe import InvestmentUniverse
from optifolio.models.asset import FinnhubAssetModel

alpaca_market_data = FinnhubClient()


@pytest.mark.vcr()
def test_get_asset_profile() -> None:
    """Test get_asset_profile method."""
    asset = alpaca_market_data.get_asset_profile(
        ticker="AAPL",
    )
    assert isinstance(asset, FinnhubAssetModel)


@pytest.mark.vcr()
def test_get_companies_profiles(
    test_tickers: tuple[str, ...],
) -> None:
    """Test get_companies_profiles method."""
    assets = alpaca_market_data.get_companies_profiles(
        tickers=test_tickers,
    )
    assert isinstance(assets, list)


@vcr.use_cassette("tests/market/cassettes/test_get_companies_profiles.yaml")
def test_get_companies_df(
    test_tickers: tuple[str, ...],
) -> None:
    """Test get_companies_df method."""
    assets = alpaca_market_data.get_companies_df(
        tickers=test_tickers,
    )
    assert isinstance(assets, pd.DataFrame)


@pytest.mark.vcr()
def test_get_companies_with_sleep() -> None:
    """Test get_companies_with_sleep method with Nasdaq tickers."""
    test_tickers = InvestmentUniverse(name=UniverseName.NASDAQ).tickers[:60]
    time.sleep = Mock()
    with pytest.raises(finnhub.FinnhubAPIException, match="API limit reached"):
        alpaca_market_data.get_companies_profiles(
            tickers=test_tickers,
        )
    time.sleep.assert_called()
