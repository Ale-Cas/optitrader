"""Configurations, mocking and fixtures for the database."""

from unittest.mock import MagicMock, Mock

import pytest

from optitrader.config import SETTINGS
from optitrader.market.db.database import MarketDB
from optitrader.market.db.models import Asset, AssetClass, AssetExchange, AssetStatus


@pytest.fixture
def asset() -> Asset:
    """Mock market database."""
    return Asset(
        _id=123,
        ticker="TEST",
        name="TEST",
        sector="TEST",
        industry="TEST",
        website="TEST",
        business_summary="TEST",
        number_of_shares=123,
        country="TEST",
        currency="TEST",
        logo="TEST",
        ipo="12/12/2012",
        tradable=True,
        marginable=True,
        fractionable=True,
        status=AssetStatus.ACTIVE,
        exchange=AssetExchange.NYSE,
        asset_class=AssetClass.US_EQUITY,
        updated_at="12/12/2012",
        updated_by="TEST",
    )


@pytest.fixture
def db() -> MarketDB:
    """Market database fixture."""
    _db = MarketDB(uri=SETTINGS.DB_URI_TEST)
    _db.drop_tables()
    _db.create_tables()
    return _db


@pytest.fixture
def mock_db(db: MarketDB) -> MarketDB:
    """Mock market database."""
    _db = MagicMock(spec=db)
    _db.drop_tables = Mock()  # type: ignore
    _db.create_tables = Mock()  # type: ignore
    _db.session.commit = Mock()  # type: ignore
    _db.session.rollback = Mock()  # type: ignore
    return _db
