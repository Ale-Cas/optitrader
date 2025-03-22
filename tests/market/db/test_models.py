"""Test database module."""

from optitrader.market.db.models import Asset


def test_asset_repr(asset: Asset) -> None:
    """Test asser repr."""
    assert isinstance(repr(asset), str)


def test_asset_to_dict(asset: Asset) -> None:
    """Test asser repr."""
    assert isinstance(asset.to_dict(), dict)
