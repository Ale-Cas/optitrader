"""Configurations, mocking and fixtures for the database."""
from unittest.mock import Mock

import pytest

from optifolio.market.db.database import MarketDB


@pytest.fixture(scope="module")
def db() -> MarketDB:
    """Market database fixture."""
    _db = MarketDB(uri="sqlite:///test.db")
    _db.drop_tables()
    _db.create_tables()
    return _db


@pytest.fixture(scope="module")
def mock_db() -> MarketDB:
    """Mock market database."""
    _db = MarketDB(uri="sqlite:///mock.db")
    _db.drop_tables = Mock()  # type: ignore
    _db.create_tables = Mock()  # type: ignore
    _db.session.commit = Mock()  # type: ignore
    _db.session.rollback = Mock()  # type: ignore
    return _db
