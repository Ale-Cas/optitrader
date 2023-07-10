"""Test enums."""

from optifolio.enums import ConstraintName


def test_constraint_name_iter() -> None:
    """Test ConstraintName."""
    assert isinstance(ConstraintName.get_values_list(), list)
    assert isinstance(ConstraintName.get_names_list(), list)
