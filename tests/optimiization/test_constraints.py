"""Test objectives map."""

import cvxpy as cp
import pytest

from optitrader.enums.optimization import ConstraintName
from optitrader.optimization.constraints import (
    ConstraintsMap,
    NumberOfAssetsConstraint,
    SumToOneConstraint,
    UnboundedConstraint,
    WeightsConstraint,
)


def test_unbounded_constr() -> None:
    """Test unbounded constraint."""
    assert isinstance(
        UnboundedConstraint(ConstraintName.SUM_TO_ONE).get_constraints_list(cp.Variable()), list
    )


def test_constraints_map() -> None:
    """Test the ConstraintsMap initialization without constraints and add financials."""
    constr_map = ConstraintsMap()
    constr_map.add_constraint(name=ConstraintName.NUMER_OF_ASSETS)
    assert isinstance(constr_map.constraints[0], NumberOfAssetsConstraint)


def test_add_constraint() -> None:
    """Test the ConstraintsMap initialization without constraints and add financials."""
    constr_map = ConstraintsMap()
    name = ConstraintName.NUMER_OF_ASSETS
    constr_map.add_constraint(name)
    constr_map.add_constraint(name)
    assert constr_map.constraints[0].name == name
    assert isinstance(constr_map.constraints[0], NumberOfAssetsConstraint)
    assert len(constr_map.constraints) == 1


def test_constraints_map_with_names() -> None:
    """Test the ConstraintsMap initialization with constraints."""
    constr_map = ConstraintsMap(
        constraint_names=[ConstraintName.SUM_TO_ONE, ConstraintName.LONG_ONLY]
    )
    assert isinstance(constr_map.constraints[0], SumToOneConstraint)


def test_constraints_map_with_bounds() -> None:
    """Test the ConstraintsMap initialization without constraints and add financials."""
    constr_map = ConstraintsMap(
        constraint_names=[ConstraintName.SUM_TO_ONE, ConstraintName.LONG_ONLY]
    )
    constr_map.add_constraint(name=ConstraintName.WEIGHTS_PCT)
    constr_map.set_constraint_bounds(name=ConstraintName.WEIGHTS_PCT, lower_bound=1)
    constr = constr_map.get_constraint_by_name(name=ConstraintName.WEIGHTS_PCT)
    assert isinstance(constr, WeightsConstraint)
    assert constr.lower_bound == 1


def test_constraints_map_with_assets_bounds() -> None:
    """Test the ConstraintsMap initialization without constraints and add financials."""
    constr_map = ConstraintsMap(constraint_names=[ConstraintName.SUM_TO_ONE])
    lb = 3
    constr_map.set_constraint_bounds(name=ConstraintName.NUMER_OF_ASSETS, lower_bound=lb)
    constr = constr_map.get_constraint_by_name(name=ConstraintName.NUMER_OF_ASSETS)
    assert isinstance(constr, NumberOfAssetsConstraint)
    assert constr.lower_bound == lb


def test_get_constraint_by_name() -> None:
    """Test getting the by_name for a certain constraint."""
    constr_map = ConstraintsMap(
        constraint_names=[ConstraintName.SUM_TO_ONE, ConstraintName.LONG_ONLY]
    )
    assert isinstance(
        constr_map.get_constraint_by_name(ConstraintName.SUM_TO_ONE), UnboundedConstraint
    )


def test_get_constraint_by_name_assertion_error() -> None:
    """Test getting the by_name for a certain constraint."""
    constr_map = ConstraintsMap()
    with pytest.raises(AssertionError):
        constr_map.get_constraint_by_name(ConstraintName.SUM_TO_ONE)


def test_get_constraint_docs() -> None:
    """Test getting the docs for a certain constraint."""
    constr_map = ConstraintsMap(
        constraint_names=[ConstraintName.SUM_TO_ONE, ConstraintName.LONG_ONLY]
    )
    constr_doc = constr_map.get_constr_doc(ConstraintName.SUM_TO_ONE)
    assert isinstance(constr_doc, str)
    assert constr_doc == SumToOneConstraint.__doc__


def test_reset_constraint_names() -> None:
    """Test the ConstraintsMap initialization without constraints and add financials."""
    constr_map = ConstraintsMap()
    constraint_names = [ConstraintName.SUM_TO_ONE, ConstraintName.LONG_ONLY]
    constr_map.reset_constraint_names(constraint_names=constraint_names)
    assert constr_map.constraints_names == constraint_names
