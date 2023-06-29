"""Objectives."""
from abc import ABCMeta, abstractmethod

import cvxpy as cp

from optifolio.enums import ConstraintName


class PortfolioConstraint(metaclass=ABCMeta):
    """Objective function abstract class."""

    def __init__(self, name) -> None:
        self.name = name

    @abstractmethod
    def get_constraints_list(self, weights_variable: cp.Variable) -> list[cp.Constraint]:
        """Get optimization matrices."""


class NoShortSellConstraint(PortfolioConstraint):
    """NoShortSell constraint."""

    def __init__(self) -> None:
        super().__init__(name=ConstraintName.LONG_ONLY)

    def get_constraints_list(self, weights_variable: cp.Variable) -> list[cp.Constraint]:
        """Get no short sell constraint matrices."""
        return [weights_variable >= 0]


class SumToOneConstraint(PortfolioConstraint):
    """SumToOne constraint."""

    def __init__(self) -> None:
        super().__init__(name=ConstraintName.SUM_TO_ONE)

    def get_constraints_list(self, weights_variable: cp.Variable) -> list[cp.Constraint]:
        """Get sum to one constraint matrices."""
        return [cp.sum(weights_variable) == 1]


class NumberOfAssetsConstraint(PortfolioConstraint):
    """NumberOfAssets constraint."""

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


class WeightsConstraint(PortfolioConstraint):
    """Weights percentage constraint."""

    def __init__(
        self,
        lower_bound: int | None = None,
        upper_bound: int | None = None,
    ) -> None:
        super().__init__(name=ConstraintName.NUMER_OF_ASSETS)
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


constraint_mapping: dict[ConstraintName, PortfolioConstraint] = {
    ConstraintName.SUM_TO_ONE: SumToOneConstraint(),
    ConstraintName.LONG_ONLY: NoShortSellConstraint(),
    ConstraintName.NUMER_OF_ASSETS: NumberOfAssetsConstraint(),
    ConstraintName.WEIGHTS_PCT: WeightsConstraint(),
}
