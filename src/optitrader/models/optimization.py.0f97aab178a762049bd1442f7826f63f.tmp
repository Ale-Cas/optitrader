"""Base models for the optimization API router."""


from collections import OrderedDict
from datetime import date, datetime, timedelta

from optitrader.config import SETTINGS
from optitrader.enums import ConstraintName
from optitrader.market.investment_universe import UniverseName
from optitrader.models.base import CustomBaseModel as BaseModel
from optitrader.optimization.constraints import (
    ConstraintsMap,
    PortfolioConstraint,
)
from optitrader.optimization.objectives import (
    ObjectiveName,
    ObjectivesMap,
    ObjectiveValue,
    PortfolioObjective,
)


class ObjectiveModel(BaseModel):
    """Objective model for the opt request."""

    _obj_map: ObjectivesMap = ObjectivesMap()
    name: ObjectiveName
    weight: float

    def to_ptf_objective(self) -> PortfolioObjective:
        """Parse to objective."""
        return self._obj_map.to_objective(name=self.name, weight=self.weight)


class ConstraintModel(BaseModel):
    """Constraint model for the opt request."""

    _constr_map: ConstraintsMap = ConstraintsMap()
    name: ConstraintName

    def to_ptf_constraint(self) -> PortfolioConstraint:
        """Parse to constraint."""
        return self._constr_map.to_constraint(self.name)


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
    weights_tolerance: float | None = SETTINGS.SUM_WEIGHTS_TOLERANCE


class OptimizationResponse(BaseModel):
    """Optimization response body."""

    weights: OrderedDict[str, float]
    objective_values: list[ObjectiveValue]
