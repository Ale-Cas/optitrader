"""Portfolio optimization problem module."""
import logging
from enum import Enum
from typing import Any

import cvxpy as cp
import pandas as pd

from optitrader.config import SETTINGS
from optitrader.enums import ConstraintName
from optitrader.enums.optimization import ObjectiveName
from optitrader.optimization.constraints import PortfolioConstraint
from optitrader.optimization.objectives import (
    FinancialsObjectiveFunction,
    ObjectivesMap,
    ObjectiveValue,
    OptimizationVariables,
    PortfolioObjective,
)
from optitrader.portfolio import Portfolio

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class _CVXPYSolver(str, Enum):
    """CVXPY supported solvers."""

    ECOS = "ECOS"
    SCS = "SCS"
    OSQP = "OSQP"


class Solver:
    """Portfolio optimization solver."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objectives: list[PortfolioObjective],
        constraints: list[PortfolioConstraint],
        financials_df: pd.DataFrame | None = None,
    ) -> None:
        if returns.isna().sum().sum():
            raise AssertionError("Passed `returns` contains NaN.")
        self.returns = returns
        if any(isinstance(o, FinancialsObjectiveFunction) for o in objectives):
            assert isinstance(
                financials_df, pd.DataFrame
            ), "You must pass the `financials_df` parameter."
            if financials_df.isna().sum().sum():
                values_per_column = 4
                selected_values = {}
                try:
                    for column in financials_df.columns:
                        non_null_values = (
                            financials_df[column].dropna().iloc[:values_per_column].tolist()
                        )
                        if len(non_null_values) == values_per_column:
                            selected_values[column] = non_null_values
                        else:
                            log.warning(
                                f"{column} with {len(non_null_values)} instead of {values_per_column} dates of financial statements data. Replacing with 0s."
                            )
                            selected_values[column] = [
                                -1e12 for _ in range(values_per_column)
                            ]  # penalize missing data
                    financials_df = pd.DataFrame(selected_values)
                except Exception as e:
                    raise AssertionError("Passed `financials_df` contains NaN.") from e
            financials_df = financials_df.pct_change().iloc[1:].fillna(0).T
            assert not financials_df.empty
        self.financials_df = financials_df
        self.objectives = objectives
        self.constraints = constraints
        self._universe = list(self.returns.columns)
        self._objectives_map = ObjectivesMap(objectives)

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
                returns=self.financials_df
                if (
                    isinstance(obj_fun, FinancialsObjectiveFunction)
                    or obj_fun.name == ObjectiveName.FINANCIALS
                )
                else self.returns,
                weights_variable=weights_variable,
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
        weights_tolerance: float | None = SETTINGS.SUM_WEIGHTS_TOLERANCE,
        cvxpy_solver: _CVXPYSolver = _CVXPYSolver.ECOS,
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
        try:
            problem.solve(solver=cvxpy_solver.value, **kwargs)
        except cp.SolverError as se:
            log.warning(se)
            # try with default solver configuration
            problem.solve()
        if problem.status != "optimal":
            raise AssertionError(f"Problem status is not optimal but: {problem.status}")
        weights_series = pd.Series(dict(zip(self._universe, weights_var.value, strict=True)))
        if ConstraintName.SUM_TO_ONE in [c.name for c in self.constraints]:
            assert 1 - weights_series.sum() <= SETTINGS.SUM_WEIGHTS_TOLERANCE
        elif ConstraintName.LONG_ONLY in [c.name for c in self.constraints]:
            assert all(weights_series >= 0)
        if weights_tolerance is not None:
            weights_series[abs(weights_series) < weights_tolerance] = 0.0
        return Portfolio(
            weights=weights_series,
            objective_values=[
                ObjectiveValue(
                    name=cvxpy_obj.name,
                    value=cvxpy_obj.minimize.value,
                    weight=self._objectives_map.get_objective_by_name(cvxpy_obj.name).weight,
                )
                for cvxpy_obj in cvxpy_objectives
            ],
            created_at=created_at,
        )
