"""Base models for the optimization API router."""


from collections import OrderedDict
from datetime import date, datetime, timedelta

from optifolio.enums import ConstraintName
from optifolio.market.investment_universe import UniverseName
from optifolio.models.base import CustomBaseModel as BaseModel
from optifolio.optimization.constraints import (
    PortfolioConstraint,
    constraint_mapping,
)
from optifolio.optimization.objectives import (
    ObjectiveName,
    ObjectiveValue,
    PortfolioObjective,
    objective_mapping,
)


class ObjectiveModel(BaseModel):
    """Objective model for the opt request."""

    name: ObjectiveName
    weight: float

    def to_ptf_objective(self) -> PortfolioObjective:
        """Parse to objective."""
        return objective_mapping[self.name]


class ConstraintModel(BaseModel):
    """Constraint model for the opt request."""

    name: ConstraintName

    def to_ptf_constraint(self) -> PortfolioConstraint:
        """Parse to constraint."""
        return constraint_mapping[self.name]


class OptimizationRequest(BaseModel):
    """Optimization request body."""

    tickers: tuple[str, ...] | None
    universe_name: UniverseName | None
    start_date: date = datetime.utcnow().date() - timedelta(days=365 * 2)
    end_date: date = datetime.utcnow().date() - timedelta(days=1)
    objectives: list[ObjectiveModel]
    constraints: list[ConstraintModel] = [  # noqa: RUF012
        ConstraintModel(name=ConstraintName.SUM_TO_ONE),
        ConstraintModel(name=ConstraintName.LONG_ONLY),
    ]
    weights_tolerance: float | None = 0.0001


class OptimizationResponse(BaseModel):
    """Optimization response body."""

    weights: OrderedDict[str, float]
    objective_values: list[ObjectiveValue]
