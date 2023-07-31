"""Test optitrader."""

import pytest

import optitrader


@pytest.mark.timeout(1)
def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(optitrader.__name__, str)
