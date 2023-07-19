"""Test market_data module."""
import pandas as pd
import pytest
import vcr
from alpaca.trading import Asset as AlpacaAsset

from optifolio.enums import UniverseName
from optifolio.market import InvestmentUniverse, MarketData
from optifolio.market.base_data_provider import BaseDataProvider
from optifolio.market.db.database import MarketDB
from optifolio.models import AssetModel


def test_base_provider() -> None:
    """Test BaseDataProvider."""
    with pytest.raises(TypeError, match="Protocols cannot be instantiated"):
        BaseDataProvider()  # type: ignore
    with pytest.raises(TypeError, match="Protocols cannot be instantiated"):
        super(BaseDataProvider, BaseDataProvider()).__init__()  # type: ignore


def test_use_db() -> None:
    """Test BaseDataProvider."""
    assert isinstance(MarketData(use_db=True)._db, MarketDB)
    with pytest.raises(AttributeError, match="has no attribute"):
        MarketData(use_db=False)._db  # noqa: B018


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


@pytest.mark.vcr()
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
def test_get_tradable_tickers(
    market_data: MarketData,
) -> None:
    """Test get_tradable_tickers method."""
    tickers = market_data.get_tradable_tickers()
    assert isinstance(tickers, tuple)
    assert isinstance(tickers[0], str)
    assert all(t.isupper() for t in tickers)


@pytest.mark.vcr()
def test_get_asset_by_name(
    market_data: MarketData,
) -> None:
    """Test get_asset_by_name method."""
    asset = market_data.get_asset_by_name(
        name="Apple",
    )
    assert isinstance(asset, AlpacaAsset)


def test_get_asset_from_ticker_error(
    market_data: MarketData,
) -> None:
    """Test get_asset_from_ticker method."""
    asset = market_data._get_asset_from_ticker(
        ticker="INVALID",
    )
    assert asset is None


@pytest.mark.vcr()
def test_get_asset(
    market_data: MarketData,
) -> None:
    """Test get_asset_from_ticker method."""
    asset = market_data.get_asset_from_ticker(
        ticker="AAPL",
    )
    assert isinstance(asset, AssetModel)


@pytest.mark.vcr()
def test_get_asset_nodb(
    market_data_nodb: MarketData,
) -> None:
    """Test get_asset_from_ticker method."""
    asset = market_data_nodb.get_asset_from_ticker(
        ticker="AAPL",
    )
    assert isinstance(asset, AssetModel)


def test_get_assets(
    market_data: MarketData,
) -> None:
    """Test get_assets method."""
    assets = market_data.get_assets()
    assert isinstance(assets, list)


def test_get_financials(
    market_data: MarketData,
) -> None:
    """Test get_total_returns method."""
    fin_df = market_data.get_financials(
        ticker="AAPL",
    )
    assert isinstance(fin_df, pd.DataFrame)


def test_investment_universe_with_top_market_cap(
    market_data: MarketData,
) -> None:
    """Test the investment universe initialization with the top_market_cap."""
    _top = 2

    tickers = market_data.get_top_market_cap_tickers(
        top=_top, tickers=InvestmentUniverse(name=UniverseName.FAANG).tickers
    )
    assert len(tickers) == _top
