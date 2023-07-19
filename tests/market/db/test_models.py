"""Test database module."""

import pytest

from optifolio.market.db.models import Asset, AssetClass, AssetExchange, AssetStatus


@pytest.fixture()
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


def test_asset_repr(asset: Asset) -> None:
    """Test asser repr."""
    assert isinstance(repr(asset), str)


def test_asset_to_dict(asset: Asset) -> None:
    """Test asser repr."""
    assert isinstance(asset.to_dict(), dict)
