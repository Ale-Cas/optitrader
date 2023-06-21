"""Test optifolio."""

import optifolio


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(optifolio.__name__, str)
