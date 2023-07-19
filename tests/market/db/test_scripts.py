"""Test the scripts for the database creation."""
from unittest.mock import Mock

import pytest

from optifolio.market.db.database import MarketDB
from optifolio.market.db.scripts.create_assets_table import main
from optifolio.market.market_data import MarketData
from optifolio.models.asset import AssetModel


@pytest.mark.timeout(10)
def test_create_assets_table(market_data_nodb: MarketData, db: MarketDB) -> None:
    """Create assets table script."""
    ticker = "AAPL"
    market_data_nodb.get_tradable_tickers = Mock(return_value=[ticker])  # type: ignore
    main(db=db, md=market_data_nodb)
    asset = db.get_asset(ticker)
    assert isinstance(asset, AssetModel)


# @pytest.mark.timeout(10)
def test_create_assets_table_errors(market_data_nodb: MarketData, mock_db: MarketDB) -> None:
    """Create assets table script."""
    market_data_nodb.get_tradable_tickers = Mock(return_value=["AAPL"])  # type: ignore
    mock_db.write_assets = Mock(side_effect=AssertionError("Test"))  # type: ignore
    main(db=mock_db, md=market_data_nodb)
    assert mock_db.session.rollback.mock_calls  # type: ignore
