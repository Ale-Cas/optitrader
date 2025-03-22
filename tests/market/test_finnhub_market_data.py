"""Test finnhub_market_data module."""

from unittest.mock import patch

import pandas as pd
import pytest
import vcr

from optitrader.market.finnhub_market_data import FinnhubClient
from optitrader.models.asset import FinnhubAssetModel


@pytest.fixture(scope="session")
def finnhub_client() -> FinnhubClient:
    """Finnhub test client."""
    return FinnhubClient()


def test_get_asset_profile_key_error(finnhub_client: FinnhubClient) -> None:
    """Test get_asset_profile method."""
    with patch("finnhub.Client.company_profile2", return_value={}), pytest.raises(KeyError):
        finnhub_client.get_asset_profile(
            ticker="INVALID",
        )


@pytest.mark.vcr
def test_get_asset_profile(finnhub_client: FinnhubClient) -> None:
    """Test get_asset_profile method."""
    asset = finnhub_client.get_asset_profile(
        ticker="AAPL",
    )
    assert isinstance(asset, FinnhubAssetModel)


@pytest.mark.vcr
def test_get_companies_profiles(
    finnhub_client: FinnhubClient,
    test_tickers: tuple[str, ...],
) -> None:
    """Test get_companies_profiles method."""
    assets = finnhub_client.get_companies_profiles(
        tickers=test_tickers,
    )
    assert isinstance(assets, list)


def test_get_companies_profiles_key_error(
    finnhub_client: FinnhubClient,
    test_tickers: tuple[str, ...],
) -> None:
    """Test get_companies_profiles method."""
    with patch("finnhub.Client.company_profile2", return_value={}):
        assets = finnhub_client.get_companies_profiles(
            tickers=test_tickers,
        )
        assert isinstance(assets, list)
        assert not assets


@vcr.use_cassette("tests/market/cassettes/test_get_companies_profiles.yaml")
def test_get_companies_df(
    finnhub_client: FinnhubClient,
    test_tickers: tuple[str, ...],
) -> None:
    """Test get_companies_df method."""
    assets = finnhub_client.get_companies_df(
        tickers=test_tickers,
    )
    assert isinstance(assets, pd.DataFrame)
