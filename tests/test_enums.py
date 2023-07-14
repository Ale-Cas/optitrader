"""Test enums."""

import pytest

from optifolio.enums import ConstraintName
from optifolio.enums.iterable import IterEnum


def test_constraint_name_iter() -> None:
    """Test ConstraintName."""
    assert isinstance(ConstraintName.get_values_list(), list)
    assert isinstance(ConstraintName.get_names_list(), list)


def test_invalid_value() -> None:
    """Test value error."""
    with pytest.raises(ValueError, match="Value not found in the Enum"):
        IterEnum.get_index_of_value("INVALID")
