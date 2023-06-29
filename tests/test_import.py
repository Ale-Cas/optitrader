"""Test optifolio."""

import pytest

import optifolio


@pytest.mark.timeout(1)
def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(optifolio.__name__, str)
