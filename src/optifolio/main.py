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
    """
    Optifolio main class.

    Attributes
    ----------
    `investment_universe`: InvestmentUniverse
        The investment universe to consider.
    `objectives`: list[PortfolioObjective]
        The objectives of the optimal portfolio.
    `constraints`: list[PortfolioConstraint]
        The constraints of the optimal portfolio.
    `market_data`: MarketData
        The market data instance to get the data from,
        you can pass your own with your API keys and preferred data provider.
    """

    def __init__(
        self,
        objectives: list[PortfolioObjective],
        universe_name: UniverseName | None = None,
        tickers: tuple[str, ...] | None = None,
        constraints: list[PortfolioConstraint] | None = None,
        market_data: MarketData | None = None,
    ) -> None:
        """
        Initialize optifolio instance.

        Parameters
        ----------
        `objectives`: list[PortfolioObjective]
            The objectives of the optimal portfolio.
        `universe_name`: UniverseName | None = None
            The name of investment universe to consider. Mutually exclusive with tickers.
        `tickers`: tuple[str] | None = None
            The tickers investment universe to consider. Mutually exclusive with universe_name.
        `constraints`: list[PortfolioConstraint] | None = None
            The constraints of the optimal portfolio.
        `market_data`: MarketData | None = None
            The market data instance to get the data from,
            you can pass your own with your API keys and preferred data provider.
        """
        self.investment_universe = InvestmentUniverse(tickers=tickers, name=universe_name)
        self.objectives = objectives
        self.constraints = constraints or [SumToOneConstraint(), NoShortSellConstraint()]
        self.market_data = market_data or MarketData()

    def solve(
        self,
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        weights_tolerance: float | None = 0.000001,
    ) -> Portfolio:
        """
        Solve the optimization problem and return the optimal portfolio.

        Parameters
        ----------
        `start_date`: pd.Timestamp
            Starting date of the optimization.
        `end_date`: pd.Timestamp
            Last date for the optimization.
        `weights_tolerance`: float
            Weights less than this tolerance are considered zeros.

        Returns
        -------
        `opt_ptf`: Portfolio
            The optimal portfolio from the Solver.
        """
        return Solver(
            returns=self.market_data.get_total_returns(
                tickers=self.investment_universe.tickers,
                start_date=start_date or end_date - pd.Timedelta(days=365 * 2),
                end_date=end_date,
            ),
            constraints=self.constraints,
            objectives=self.objectives,
        ).solve(
            weights_tolerance=weights_tolerance,
        )
