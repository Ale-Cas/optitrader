"""Objectives."""
from abc import ABCMeta, abstractmethod

import cvxpy as cp

from optitrader.enums import ConstraintName


class PortfolioConstraint(metaclass=ABCMeta):
    """Objective function abstract class."""

    def __init__(self, name: ConstraintName) -> None:
        self.name = name

    @abstractmethod
    def get_constraints_list(self, weights_variable: cp.Variable) -> list[cp.Constraint]:
        """Get optimization matrices."""


class UnboundedConstraint(PortfolioConstraint):
    """UnboundedConstraint constraint."""

    def get_constraints_list(self, weights_variable: cp.Variable) -> list[cp.Constraint]:
        """Get no short sell constraint matrices."""
        return []


class BoundedConstraint(PortfolioConstraint):
    """Bounded constraint."""

    def __init__(
        self,
        name: ConstraintName,
        lower_bound: int | None = None,
        upper_bound: int | None = None,
    ) -> None:
        super().__init__(name=name)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def set_bounds(
        self,
        lower_bound: int | None = None,
        upper_bound: int | None = None,
    ) -> None:
        """Set lower_bound."""
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound


class NoShortSellConstraint(UnboundedConstraint):
    """NoShortSell constraint."""

    def __init__(self) -> None:
        super().__init__(name=ConstraintName.LONG_ONLY)

    def get_constraints_list(self, weights_variable: cp.Variable) -> list[cp.Constraint]:
        """Get no short sell constraint matrices."""
        return [weights_variable >= 0]


class SumToOneConstraint(UnboundedConstraint):
    """SumToOne constraint."""

    def __init__(self) -> None:
        super().__init__(name=ConstraintName.SUM_TO_ONE)

    def get_constraints_list(self, weights_variable: cp.Variable) -> list[cp.Constraint]:
        """Get sum to one constraint matrices."""
        return [cp.sum(weights_variable) == 1]


class NumberOfAssetsConstraint(BoundedConstraint):
    """
    NumberOfAssets constraint.

    TODO: See other implementation https://groups.google.com/g/cvxpy/c/l9NetwWXQ-k
    """

    def __init__(
        self,
        lower_bound: int | None = None,
        upper_bound: int | None = None,
    ) -> None:
        super().__init__(name=ConstraintName.NUMER_OF_ASSETS)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def get_constraints_list(self, weights_variable: cp.Variable) -> list[cp.Constraint]:
        """Get sum to one constraint matrices."""
        w_bool = cp.Variable(weights_variable.shape, boolean=True)
        constraints = [weights_variable - w_bool <= 0]
        if self.lower_bound is not None:
            constraints.append(cp.sum(w_bool) >= self.lower_bound)
        if self.upper_bound is not None:
            constraints.append(cp.sum(w_bool) <= self.upper_bound)
        return constraints


class WeightsConstraint(BoundedConstraint):
    """Weights percentage constraint."""

    def __init__(
        self,
        lower_bound: int | None = None,
        upper_bound: int | None = None,
    ) -> None:
        super().__init__(name=ConstraintName.WEIGHTS_PCT)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def get_constraints_list(self, weights_variable: cp.Variable) -> list[cp.Constraint]:
        """Get weights constraints list."""
        _tot = 100
        constraints = []
        if self.lower_bound is not None:
            assert self.lower_bound >= 0, "The lower bound percentage cannot be less than 0."
            assert (
                self.lower_bound <= _tot
            ), f"The lower bound percentage cannot be more than {_tot}."
            constraints.append(weights_variable >= self.lower_bound / _tot)
        if self.upper_bound is not None:
            assert (
                self.upper_bound <= _tot
            ), f"The upper bound percentage cannot be more than {_tot}."
            constraints.append(weights_variable <= self.upper_bound / _tot)
        return constraints


class ConstraintsMap:
    """Constraints map."""

    def __init__(
        self,
        constraints: list[PortfolioConstraint] | None = None,
        constraint_names: list[ConstraintName] | None = None,
    ) -> None:
        self.constraint_mapping: dict[ConstraintName, UnboundedConstraint | BoundedConstraint] = {
            ConstraintName.SUM_TO_ONE: SumToOneConstraint(),
            ConstraintName.LONG_ONLY: NoShortSellConstraint(),
            ConstraintName.NUMER_OF_ASSETS: NumberOfAssetsConstraint(),
            ConstraintName.WEIGHTS_PCT: WeightsConstraint(),
        }
        self.constraints: list[PortfolioConstraint] = (
            constraints or [self.to_constraint(name) for name in constraint_names]
            if constraint_names
            else []
        )

    @property
    def constraints_names(self) -> list[str]:
        """Return the obejctives names."""
        return [o.name for o in self.constraints]

    def to_constraint(
        self,
        name: ConstraintName,
        lower_bound: int | None = None,
        upper_bound: int | None = None,
    ) -> PortfolioConstraint:
        """Get a constraint."""
        if name.is_bounded:
            constr = self.constraint_mapping[name]
            assert isinstance(constr, BoundedConstraint)
            constr.set_bounds(
                lower_bound=lower_bound,
                upper_bound=upper_bound,
            )
            return constr
        return self.constraint_mapping[name]

    def reset_constraint_names(self, constraint_names: list[ConstraintName]) -> None:
        """Reset the constraint names based on the chosen ones in streamlit."""
        self.constraints = [self.to_constraint(name) for name in constraint_names]

    def get_constraint_by_name(
        self,
        name: ConstraintName,
    ) -> PortfolioConstraint:
        """Get an constraint."""
        _objs = [o for o in self.constraints if o.name == name]
        assert len(_objs) > 0, f"Constraint {name} not in the constraints list {self.constraints}."
        return _objs[0]

    def add_constraint(
        self,
        name: ConstraintName,
        lower_bound: int | None = None,
        upper_bound: int | None = None,
    ) -> None:
        """Add an constraint to the map."""
        if name not in self.constraints_names:
            self.constraints.append(
                self.to_constraint(
                    name=name,
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                )
            )

    def get_constr_doc(
        self,
        name: ConstraintName,
    ) -> str:
        """Return the constraint docstring."""
        return (
            self.constraint_mapping[name].__doc__
            or f"{self.constraint_mapping[name].__class__.__name__} documentation."
        )

    def set_constraint_bounds(
        self,
        name: ConstraintName,
        lower_bound: int | None = None,
        upper_bound: int | None = None,
    ) -> None:
        """Set the bounds for a bounded constraint."""
        assert name.is_bounded, "This constraint has no bounds."
        assert lower_bound or upper_bound, "You must set either the lower or upper bound."
        if name in self.constraints_names:
            for constr in self.constraints:
                if name == constr.name:
                    assert isinstance(constr, BoundedConstraint)
                    constr.set_bounds(
                        lower_bound=lower_bound,
                        upper_bound=upper_bound,
                    )
        else:
            self.add_constraint(
                name=name,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
            )
