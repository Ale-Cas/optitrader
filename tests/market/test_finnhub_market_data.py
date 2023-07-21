"""Test finnhub_market_data module."""
import time
from unittest.mock import Mock, patch

import finnhub
import pandas as pd
import pytest
import vcr

from optifolio.enums.market import UniverseName
from optifolio.market.finnhub_market_data import FinnhubClient
from optifolio.market.investment_universe import InvestmentUniverse
from optifolio.models.asset import FinnhubAssetModel

finnhub_client = FinnhubClient()
mock_finnhub_client = FinnhubClient()


@pytest.mark.vcr()
def test_get_asset_profile() -> None:
    """Test get_asset_profile method."""
    asset = finnhub_client.get_asset_profile(
        ticker="AAPL",
    )
    assert isinstance(asset, FinnhubAssetModel)


def test_get_asset_profile_key_error() -> None:
    """Test get_asset_profile method."""
    with patch("finnhub.Client.company_profile2", return_value={}):
        asset = mock_finnhub_client.get_asset_profile(
            ticker="AAPL",
        )
        assert asset is None


@pytest.mark.vcr()
def test_get_companies_profiles(
    test_tickers: tuple[str, ...],
) -> None:
    """Test get_companies_profiles method."""
    assets = finnhub_client.get_companies_profiles(
        tickers=test_tickers,
    )
    assert isinstance(assets, list)


def test_get_companies_profiles_key_error(
    test_tickers: tuple[str, ...],
) -> None:
    """Test get_companies_profiles method."""
    with patch("finnhub.Client.company_profile2", return_value={}):
        assets = mock_finnhub_client.get_companies_profiles(
            tickers=test_tickers,
        )
        assert isinstance(assets, list)
        assert not assets


@vcr.use_cassette("tests/market/cassettes/test_get_companies_profiles.yaml")
def test_get_companies_df(
    test_tickers: tuple[str, ...],
) -> None:
    """Test get_companies_df method."""
    assets = finnhub_client.get_companies_df(
        tickers=test_tickers,
    )
    assert isinstance(assets, pd.DataFrame)


@pytest.mark.vcr()
def test_get_companies_with_sleep() -> None:
    """Test get_companies_with_sleep method with Nasdaq tickers."""
    test_tickers = InvestmentUniverse(name=UniverseName.NASDAQ).tickers
    time.sleep = Mock()
    with pytest.raises(finnhub.FinnhubAPIException, match="API limit reached"):
        finnhub_client.get_companies_profiles(
            tickers=test_tickers,
        )
    time.sleep.assert_called()
