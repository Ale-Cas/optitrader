"""Objective function module."""
from abc import ABCMeta, abstractmethod

import cvxpy as cp
import pandas as pd
from pydantic import BaseModel

from optifolio.enums import ObjectiveName


class _BaseObjectiveModel(BaseModel):
    """Base objective model to avoid duplication."""

    name: ObjectiveName


class ObjectiveValue(_BaseObjectiveModel):
    """Model to represent the mapping of an objective to its optimal value."""

    value: float


class OptimizationVariables(_BaseObjectiveModel):
    """Objective optimization variables."""

    minimize: cp.Minimize

    class Config:
        """Configuration."""

        arbitrary_types_allowed = True


class PortfolioObjective(metaclass=ABCMeta):
    """Objective function abstract class."""

    def __init__(
        self,
        name: ObjectiveName,
        weight: float = 1.0,
    ) -> None:
        self.weight = weight
        self.name = name

    @abstractmethod
    def get_objective_and_auxiliary_constraints(
        self,
        returns: pd.DataFrame,
        weights_variable: cp.Variable,
    ) -> tuple[OptimizationVariables, list[cp.Constraint]]:
        """Get optimization matrices."""


class CVaRObjectiveFunction(PortfolioObjective):
    """CVaR objective function."""

    def __init__(
        self,
        confidence_level: float = 0.7,
        weight: float = 1.0,
    ) -> None:
        super().__init__(weight=weight, name=ObjectiveName.CVAR)
        self.confidence_level = confidence_level

    def get_objective_and_auxiliary_constraints(
        self,
        returns: pd.DataFrame,
        weights_variable: cp.Variable,
    ) -> tuple[OptimizationVariables, list[cp.Constraint]]:
        """Get CVaR optimization matrices."""
        rets_vals = returns.values
        n_obs = rets_vals.shape[0]
        losses_minus_var = cp.Variable(n_obs, nonneg=True)
        value_at_risk = cp.Variable(1)
        objective_function = value_at_risk + 1 / ((1 - self.confidence_level) * n_obs) * cp.sum(
            losses_minus_var
        )
        return (
            OptimizationVariables(
                name=self.name, minimize=cp.Minimize(self.weight * objective_function)
            ),
            [-rets_vals @ weights_variable - value_at_risk - losses_minus_var <= 0],
        )


class CovarianceObjectiveFunction(PortfolioObjective):
    """Variance objective function."""

    def __init__(
        self,
        weight: float = 1.0,
    ) -> None:
        super().__init__(weight=weight, name=ObjectiveName.COVARIANCE)

    def get_objective_and_auxiliary_constraints(
        self,
        returns: pd.DataFrame,
        weights_variable: cp.Variable,
    ) -> tuple[OptimizationVariables, list[cp.Constraint]]:
        """Get Variance optimization matrices."""
        # Annualize the cov mat
        sigma = 252 * returns.cov().values
        objective_function = weights_variable @ sigma @ weights_variable
        return (
            OptimizationVariables(
                name=self.name, minimize=cp.Minimize(self.weight * objective_function)
            ),
            [],
        )


class ExpectedReturnsObjectiveFunction(PortfolioObjective):
    """Expected Returns objective function."""

    def __init__(
        self,
        weight: float = 0.25,
    ) -> None:
        super().__init__(weight=weight, name=ObjectiveName.EXPECTED_RETURNS)

    def get_objective_and_auxiliary_constraints(
        self,
        returns: pd.DataFrame,
        weights_variable: cp.Variable,
    ) -> tuple[OptimizationVariables, list[cp.Constraint]]:
        """Get Expected Returns optimization matrices."""
        # Annualize expected returns and put minus in front to maximize
        exp_rets = -252 * returns.mean().values
        objective_function = weights_variable @ exp_rets
        return (
            OptimizationVariables(
                name=self.name, minimize=cp.Minimize(self.weight * objective_function)
            ),
            [],
        )


class MADObjectiveFunction(PortfolioObjective):
    """Mean Absolute Deviation objective function."""

    def __init__(
        self,
        weight: float = 1.0,
    ) -> None:
        super().__init__(weight=weight, name=ObjectiveName.MEAN_ABSOLUTE_DEVIATION)

    def get_objective_and_auxiliary_constraints(
        self,
        returns: pd.DataFrame,
        weights_variable: cp.Variable,
    ) -> tuple[OptimizationVariables, list[cp.Constraint]]:
        """Get Mean Absolute Deviation optimization matrices."""
        rets_vals = returns.values
        n_obs = rets_vals.shape[0]
        abs_devs = cp.Variable(n_obs, nonneg=True)
        rets_minus_mu = rets_vals - returns.mean().values
        objective_function = cp.sum(abs_devs) / n_obs
        return OptimizationVariables(
            name=self.name, minimize=cp.Minimize(self.weight * objective_function)
        ), [
            rets_minus_mu @ weights_variable - abs_devs <= 0,
            -rets_minus_mu @ weights_variable - abs_devs <= 0,
        ]


objective_mapping: dict[ObjectiveName, PortfolioObjective] = {
    ObjectiveName.CVAR: CVaRObjectiveFunction(),
    ObjectiveName.EXPECTED_RETURNS: ExpectedReturnsObjectiveFunction(),
    ObjectiveName.MEAN_ABSOLUTE_DEVIATION: MADObjectiveFunction(),
    ObjectiveName.COVARIANCE: CovarianceObjectiveFunction(),
}
