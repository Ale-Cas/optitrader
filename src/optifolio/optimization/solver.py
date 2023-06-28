"""Portfolio optimization problem module."""
from typing import Any

import cvxpy as cp
import pandas as pd

from optifolio.optimization.constraints import ConstraintName, PortfolioConstraint
from optifolio.optimization.objectives import (
    ObjectiveValue,
    OptimizationVariables,
    PortfolioObjective,
)
from optifolio.portfolio import Portfolio


class Solver:
    """Portfolio optimization solver."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objectives: list[PortfolioObjective],
        constraints: list[PortfolioConstraint],
    ) -> None:
        if returns.isna().sum().sum():
            raise AssertionError("Passed `returns` contains NaN.")
        self.returns = returns
        self.objectives = objectives
        self.constraints = constraints
        self._universe = list(self.returns.columns)

    def _get_cvxpy_objectives_and_constraints(
        self, weights_variable: cp.Variable
    ) -> tuple[list[OptimizationVariables], list[cp.Constraint]]:
        """Get portfolio optimization problem."""
        assert (
            self.objectives
        ), "To get a portfolio optimization problem, at least one objective is needed."
        cvxpy_objectives: list[OptimizationVariables] = []
        cvxpy_constraints: list[cp.Constraint] = []
        for obj_fun in self.objectives:
            objective, constr_list = obj_fun.get_objective_and_auxiliary_constraints(
                returns=self.returns, weights_variable=weights_variable
            )
            cvxpy_objectives.append(objective)
            cvxpy_constraints.extend(constr_list)
        for constr_fun in self.constraints:
            cvxpy_constraints.extend(
                constr_fun.get_constraints_list(weights_variable=weights_variable)
            )
        return cvxpy_objectives, cvxpy_constraints

    def solve(
        self,
        created_at: pd.Timestamp | None = None,
        weights_tolerance: float | None = 1e-6,
        **kwargs: Any,
    ) -> Portfolio:
        """Solve a portfolio optimization problem.

        Parameters
        ----------
        weights_tolerance
            An optional float, if provided the weights resulting smaller then weights_tolerance
            after an optimization will be set to 0.
        kwargs
            All the supported params of cvxpy.problems.problem.Problem.solve().
        """
        weights_var = cp.Variable(len(self._universe))
        cvxpy_objectives, cvxpy_constraints = self._get_cvxpy_objectives_and_constraints(
            weights_var
        )
        problem = cp.Problem(
            # objective=cp.sum([min_obj for obj in cvxpy_objectives for min_obj in obj.values()]),
            objective=cp.sum([obj.minimize for obj in cvxpy_objectives]),
            constraints=cvxpy_constraints,
        )
        problem.solve(**kwargs)
        if problem.status != "optimal":
            raise AssertionError(f"Problem status is not optimal but: {problem.status}")
        weights_series = pd.Series(dict(zip(self._universe, weights_var.value, strict=True)))
        if ConstraintName.SUM_TO_ONE in [c.name for c in self.constraints]:
            assert 1 - weights_series.sum() <= weights_tolerance
        elif ConstraintName.LONG_ONLY in [c.name for c in self.constraints]:
            assert all(weights_series >= 0)
        if weights_tolerance is not None:
            weights_series[abs(weights_series) < weights_tolerance] = 0.0
        return Portfolio(
            weights=weights_series,
            objective_values=[
                ObjectiveValue(name=cvxpy_obj.name, value=cvxpy_obj.minimize.value)
                for cvxpy_obj in cvxpy_objectives
            ],
            created_at=created_at,
        )
