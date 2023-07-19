"""Test database module."""

import pytest
from sqlalchemy.exc import OperationalError

from optifolio.market import MarketData
from optifolio.market.db.database import MarketDB


def test_write_assets(db: MarketDB, test_tickers: tuple[str, ...]) -> None:
    """Test to write the assets."""
    assets = MarketData().get_assets(tickers=(*test_tickers, "INVALID"))
    db.write_assets(asset_models=assets, autocommit=False)
    db.session.rollback()
    db.write_assets(asset_models=assets, autocommit=True)
    assert len(db.get_assets(tickers=test_tickers)) == len(test_tickers) - 1  # V is missing
    # try a second time for the exception handling
    db.write_assets(asset_models=assets, autocommit=True)
    assert (
        len(db.get_assets(tickers=test_tickers)) == len(test_tickers) - 1
    )  # check that the number didn't change


def test_get_tickers(db: MarketDB, test_tickers: tuple[str, ...]) -> None:
    """Test get_tickers method."""
    assets = MarketData().get_assets(tickers=test_tickers)
    db.write_assets(asset_models=assets, autocommit=True)
    tickers = db.get_tickers()
    assert isinstance(tickers, list)
    assert len(tickers) > 1
    assert isinstance(tickers[0], str)


def test_drop_tables(db: MarketDB) -> None:
    """Test drop_tables method."""
    db.drop_tables()
    with pytest.raises(OperationalError):
        db.get_assets()
