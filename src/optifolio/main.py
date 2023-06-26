"""Main module for the Optifolio class implementation."""

import pandas as pd

from optifolio.enums import UniverseName
from optifolio.market import InvestmentUniverse, MarketData
from optifolio.optimization.constraints import (
    NoShortSellConstraint,
    PortfolioConstraint,
    SumToOneConstraint,
)
from optifolio.optimization.objectives import PortfolioObjective
from optifolio.optimization.solver import Solver
from optifolio.portfolio import Portfolio


class Optifolio:
    """Optifolio main class."""

    def __init__(
        self,
        objectives: list[PortfolioObjective],
        universe_name: UniverseName | None = None,
        tickers: tuple[str, ...] | None = None,
        constraints: list[PortfolioConstraint] | None = None,
        market_data: MarketData | None = None,
    ) -> None:
        self.investment_universe = InvestmentUniverse(tickers=tickers, name=universe_name)
        self.objectives = objectives
        self.constraints = constraints or [SumToOneConstraint(), NoShortSellConstraint()]
        self.market_data = market_data or MarketData()

    def solve(
        self,
        start_date: pd.Timestamp,
        weights_tolerance: float | None = 0.000001,
    ) -> Portfolio:
        """Solve the optimization problem and return the optimal portfolio."""
        return Solver(
            returns=self.market_data.get_total_returns(
                tickers=self.investment_universe.tickers,
                start_date=start_date,
            ),
            constraints=self.constraints,
            objectives=self.objectives,
        ).solve(
            weights_tolerance=weights_tolerance,
        )
