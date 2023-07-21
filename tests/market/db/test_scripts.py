"""Test the scripts for the database creation."""
from unittest.mock import Mock

import pytest

from optifolio.market.db.database import MarketDB
from optifolio.market.db.scripts import add_asset, create_assets_table, update_number_of_shares
from optifolio.market.market_data import MarketData
from optifolio.models.asset import AssetModel


@pytest.mark.timeout(10)
def test_create_assets_table(market_data_nodb: MarketData, db: MarketDB) -> None:
    """Create assets table script."""
    ticker = "AAPL"
    market_data_nodb.get_tradable_tickers = Mock(return_value=[ticker])  # type: ignore
    create_assets_table.main(db=db, md=market_data_nodb)
    asset = db.get_asset(ticker)
    assert isinstance(asset, AssetModel)


@pytest.mark.timeout(10)
def test_create_assets_table_errors(market_data_nodb: MarketData, mock_db: MarketDB) -> None:
    """Create assets table script."""
    market_data_nodb.get_tradable_tickers = Mock(return_value=["AAPL"])  # type: ignore
    mock_db.write_assets = Mock(side_effect=AssertionError("Test"))  # type: ignore
    create_assets_table.main(db=mock_db, md=market_data_nodb)
    assert mock_db.session.rollback.mock_calls  # type: ignore


@pytest.mark.timeout(10)
def test_add_ticker(market_data_nodb: MarketData, mock_db: MarketDB, asset: AssetModel) -> None:
    """Create assets table script."""
    market_data_nodb.get_asset = Mock(return_value=asset)  # type: ignore
    mock_db.write_asset = Mock()  # type: ignore
    add_asset.main(db=mock_db, md=market_data_nodb, ticker=asset.ticker)
    mock_db.get_tickers = Mock(return_value=[asset.ticker])  # type: ignore
    add_asset.main(db=mock_db, md=market_data_nodb, ticker=asset.ticker)


@pytest.mark.timeout(10)
def test_update_number_of_shares(market_data_nodb: MarketData, mock_db: MarketDB) -> None:
    """Create assets table script."""
    mock_db.get_tickers = Mock(return_value=["AAPL"])  # type: ignore
    update_number_of_shares.main(db=mock_db, md=market_data_nodb)
