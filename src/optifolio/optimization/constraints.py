"""Objectives."""
from abc import ABCMeta, abstractmethod

import cvxpy as cp


class ConstraintFunction(metaclass=ABCMeta):
    """Objective function abstract class."""

    @abstractmethod
    def get_constraints_list(self, weights_variable: cp.Variable) -> list[cp.Constraint]:
        """Get optimization matrices."""


class NoShortSellConstraint(ConstraintFunction):
    """NoShortSell constraint."""

    def get_constraints_list(self, weights_variable: cp.Variable) -> list[cp.Constraint]:
        """Get no short sell constraint matrices."""
        return [weights_variable >= 0]


class SumToOneConstraint(ConstraintFunction):
    """SumToOne constraint."""

    def get_constraints_list(self, weights_variable: cp.Variable) -> list[cp.Constraint]:
        """Get sum to one constraint matrices."""
        return [cp.sum(weights_variable) == 1]


class NumberOfAssetsConstraint(ConstraintFunction):
    """NumberOfAssets constraint."""

    def __init__(
        self,
        lower_bound: int | None = None,
        upper_bound: int | None = None,
    ) -> None:
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
