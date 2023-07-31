"""Objective function module."""
from abc import ABCMeta, abstractmethod

import cvxpy as cp
import numpy as np
import pandas as pd
from pydantic import BaseModel

from optitrader.enums import ObjectiveName


class _BaseObjectiveModel(BaseModel):
    """Base objective model to avoid duplication."""

    name: ObjectiveName


class ObjectiveValue(_BaseObjectiveModel):
    """Model to represent the mapping of an objective to its optimal value."""

    value: float
    weight: float


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

    @abstractmethod
    def get_obj_latex(self) -> str:
        """Get objective formulation as latex."""


class CVaRObjectiveFunction(PortfolioObjective):
    """
    Conditional value at Risk objective function.

    Conditional Value at Risk (CVaR), also known as Expected Shortfall (ES),
    is a risk measure used in financial analysis and portfolio management
    to assess the potential losses beyond a specified confidence level.
    Unlike traditional risk measures such as Value at Risk (VaR)
    that focus solely on the magnitude of potential losses,
    CVaR provides additional insights by considering the severity of losses
    that occur beyond the VaR threshold.
    """

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

    def get_obj_latex(self) -> str:
        """Get objective formulation as latex."""
        return r"""
        \text{CVaR}_{\alpha}(X) = \frac{1}{1 - \alpha} \int_{\alpha}^{1} \text{VaR}_{\beta}(X) \, d\beta
        """


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

    def get_obj_latex(self) -> str:
        """Get objective formulation as latex."""
        return r"""
        \text{Var}(X) = \frac{1}{n} \sum_{i=1}^{n} (X_i - \bar{X})^2
        """


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

    def get_obj_latex(self) -> str:
        """Get objective formulation as latex."""
        return r"""
        \text{E}(R_p) = \sum_{i=1}^{n} w_i \times \text{E}(R_i)
        """


class MADObjectiveFunction(PortfolioObjective):
    """
    ### Mean Absolute Deviation objective function.

    Mean Absolute Deviation measures the average deviation of data points from the mean. It is a risk measure that focuses on the dispersion of the data.

    The formula for Mean Absolute Deviation (MAD) is given by:
    """

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

    def get_obj_latex(self) -> str:
        """Get objective formulation as latex."""
        return r"""
        \text{MAD}(X) = \frac{1}{n} \sum_{i=1}^{n} |X_i - \bar{X}|
        """


class FinancialsObjectiveFunction(PortfolioObjective):
    """
    Financials objective function.

    This objective lets you maximize one item on the financial statements, such as the net profit.
    """

    def __init__(
        self,
        weight: float = 0.25,
    ) -> None:
        super().__init__(weight=weight, name=ObjectiveName.FINANCIALS)

    def get_objective_and_auxiliary_constraints(
        self,
        returns: pd.DataFrame,
        weights_variable: cp.Variable,
    ) -> tuple[OptimizationVariables, list[cp.Constraint]]:
        """
        Get Financials optimization matrices.

        Note that the returns are actually the financials.
        """
        # Boost the financials growth and put minus in front to maximize
        objective_function = cp.sum(
            weights_variable @ -returns * 1e-4
        )  # 1e-4 is the scaling factor to compare with other objectives
        return (
            OptimizationVariables(
                name=self.name, minimize=cp.Minimize(self.weight * objective_function)
            ),
            [],
        )

    def get_obj_latex(self) -> str:
        """Get objective formulation as latex."""
        return r"""
        \text{E}(R_p) = \sum_{i=1}^{n} w_i \times R_{i,scaled}
        """


class MostDiversifiedObjectiveFunction(PortfolioObjective):
    """
    ### Most diversified portfolio (MDP) objective function.

    This objective lets you maximize the diversification ratio, that is
    the ratio of the weighted average of volatilities divided by the portfolio volatility.

    #### Mathematical Formulation:

    Let `n` be the number of assets in the portfolio.
    Let `returns` be a 2D numpy array of shape (T, n), where `T` is the number of time periods
    and `n` is the number of assets.`C` is the covariance matrix of asset returns with shape (n, n).
    `w` is a vector of portfolio weights with lenght `n`.
    `sigma` is the portfolio volatility.
    'vol' is a vector of asset volatilities with shape (n,), obtained from the diagonal elements of 'C'.
    'sum' represents the sum of elements in a vector.

    The diversification ratio (`DR`) can be formulated as follows:
    """

    def __init__(
        self,
        weight: float = 1.0,
    ) -> None:
        super().__init__(weight=weight, name=ObjectiveName.MOST_DIVERSIFIED)

    def get_objective_and_auxiliary_constraints(
        self,
        returns: pd.DataFrame,
        weights_variable: cp.Variable,
    ) -> tuple[OptimizationVariables, list[cp.Constraint]]:
        """
        Get Financials optimization matrices.

        Note that the returns are actually the financials.
        """
        # copy the weights to not modify the other weights variable
        _weights = cp.Variable(weights_variable.shape[0], nonneg=True)
        cov_matrix = returns.cov().values
        return (
            OptimizationVariables(
                name=self.name,
                minimize=cp.Minimize(_weights @ cov_matrix @ _weights),
            ),
            [_weights @ np.sqrt(cov_matrix.diagonal()) == 1],
        )

    def get_obj_latex(self) -> str:
        """Get objective formulation as latex."""
        return r"""
        DR = \frac{\sum{w * vol}}{\sqrt{w^T * C * w}}
        """


class ObjectivesMap:
    """Objectives map."""

    def __init__(
        self,
        objectives: list[PortfolioObjective] | None = None,
    ) -> None:
        self.objective_mapping: dict[ObjectiveName, type[PortfolioObjective]] = {
            ObjectiveName.CVAR: CVaRObjectiveFunction,
            ObjectiveName.EXPECTED_RETURNS: ExpectedReturnsObjectiveFunction,
            ObjectiveName.MEAN_ABSOLUTE_DEVIATION: MADObjectiveFunction,
            ObjectiveName.COVARIANCE: CovarianceObjectiveFunction,
            ObjectiveName.FINANCIALS: FinancialsObjectiveFunction,
            ObjectiveName.MOST_DIVERSIFIED: MostDiversifiedObjectiveFunction,
        }
        self.objectives: list[PortfolioObjective] = objectives or []

    @property
    def objectives_names(self) -> list[str]:
        """Return the obejctives names."""
        return [o.name for o in self.objectives]

    def to_objective(
        self,
        name: ObjectiveName,
        weight: float = 1.0,
    ) -> PortfolioObjective:
        """Get an objective."""
        return self.objective_mapping[name](weight=weight)  # type: ignore

    def reset_objectives_names(self, objectives_names: list[ObjectiveName]) -> None:
        """Reset the objective names."""
        self.objectives = [self.to_objective(name) for name in objectives_names]

    def get_objective_by_name(
        self,
        name: ObjectiveName,
    ) -> PortfolioObjective:
        """Get an objective."""
        _objs = [o for o in self.objectives if o.name == name]
        assert len(_objs) > 0, f"Objective {name} not in the objectives list {self.objectives}."
        return _objs[0]

    def add_objective(
        self,
        name: ObjectiveName,
        weight: float = 1.0,
    ) -> None:
        """Add an objective to the map."""
        if name not in self.objectives_names:
            if name == ObjectiveName.FINANCIALS:
                self.objectives.append(
                    self.to_objective(
                        name=name,
                        weight=weight,
                    )
                )
            else:
                self.objectives.append(self.to_objective(name=name, weight=weight))
        else:
            obj = self.get_objective_by_name(name)
            if obj.weight != weight:
                obj.weight = weight

    def get_obj_doc(
        self,
        name: ObjectiveName,
    ) -> str:
        """Return the objective docstring."""
        return (
            self.objective_mapping[name].__doc__
            or f"{self.objective_mapping[name].__name__} documentation."
        )

    def get_obj_latex(
        self,
        name: ObjectiveName,
    ) -> str:
        """Return the objective docstring."""
        return self.objective_mapping[name]().get_obj_latex()  # type: ignore
