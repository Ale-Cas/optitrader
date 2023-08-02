"""Main module for the optitrader class implementation."""

import pandas as pd

from optitrader.config import SETTINGS
from optitrader.enums import UniverseName
from optitrader.enums.market import BalanceSheetItem, CashFlowItem, IncomeStatementItem
from optitrader.enums.optimization import ObjectiveName
from optitrader.market import InvestmentUniverse, MarketData
from optitrader.optimization.constraints import (
    NoShortSellConstraint,
    NumberOfAssetsConstraint,
    PortfolioConstraint,
    SumToOneConstraint,
    WeightsConstraint,
)
from optitrader.optimization.objectives import PortfolioObjective
from optitrader.optimization.solver import Solver
from optitrader.portfolio import Portfolio


class Optitrader:
    """
    Optitrader main class.

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
        trading_key: str | None = SETTINGS.ALPACA_TRADING_API_KEY,
        trading_secret: str | None = SETTINGS.ALPACA_TRADING_API_SECRET,
        broker_key: str | None = SETTINGS.ALPACA_BROKER_API_KEY,
        broker_secret: str | None = SETTINGS.ALPACA_BROKER_API_SECRET,
    ) -> None:
        """
        Initialize optitrader instance.

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
        assert (
            market_data or (trading_key and trading_secret) or (broker_key and broker_secret)
        ), "You must pass either a MarketData instance, the Trading API keys or Broker API keys."
        self.market_data = market_data or MarketData(
            trading_key=trading_key,
            trading_secret=trading_secret,
            broker_key=broker_key,
            broker_secret=broker_secret,
        )

    def add_constraint(self, constraint: PortfolioConstraint) -> None:
        """Add a constraint."""
        self.constraints.append(constraint)

    def add_objective(self, objective: PortfolioObjective) -> None:
        """Add an objective."""
        self.objectives.append(objective)

    def solve(
        self,
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        weights_tolerance: float | None = 0.000001,
        num_assets: int | None = None,
        min_num_assets: int | None = None,
        max_num_assets: int | None = None,
        max_weight_pct: int | None = None,
        min_weight_pct: int | None = None,
        financial_item: IncomeStatementItem
        | CashFlowItem
        | BalanceSheetItem = IncomeStatementItem.NET_INCOME,
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
        `num_assets`: int
            The number of assets you want in the optimal portfolio.
        `min_num_assets`: int
            The minimum number of assets you want in the optimal portfolio.
        `max_num_assets`: int
            The maximum number of assets you want in the optimal portfolio.
        `max_weight_pct`: int
            The maximum weight for assets you want in the optimal portfolio.
        `min_weight_pct`: int
            The minimum weight for assets you want in the optimal portfolio.

        Returns
        -------
        `opt_ptf`: Portfolio
            The optimal portfolio from the Solver.
        """
        if num_assets:
            assert (
                not min_num_assets
            ), "Cannot provide minimum number of assets if you provided the exact number of assets."
            assert (
                not max_num_assets
            ), "Cannot provide maximum number of assets if you provided the exact number of assets."
            if num_assets == len(self.investment_universe):
                self.add_constraint(
                    WeightsConstraint(
                        lower_bound=1,  # give a minimum of 1 pct weight to each asset
                        upper_bound=max_weight_pct,
                    )
                )
            else:
                self.add_constraint(
                    NumberOfAssetsConstraint(lower_bound=num_assets, upper_bound=num_assets)
                )
        elif min_num_assets or max_num_assets:
            assert (
                not num_assets
            ), "Cannot provide exact number of assets if you provided the minimum or maximum number of assets."
            self.add_constraint(
                NumberOfAssetsConstraint(lower_bound=min_num_assets, upper_bound=max_num_assets)
            )
        elif min_weight_pct or max_weight_pct:
            self.add_constraint(
                WeightsConstraint(
                    lower_bound=min_weight_pct,
                    upper_bound=max_weight_pct,
                )
            )
        opt_ptf = Solver(
            returns=self.market_data.get_total_returns(
                tickers=self.investment_universe.tickers,
                start_date=start_date or end_date - pd.Timedelta(days=365 * 2),
                end_date=end_date,
            ),
            constraints=self.constraints,
            objectives=self.objectives,
            financials_df=self.market_data.get_multi_financials_by_item(
                tickers=self.investment_universe.tickers,
                financial_item=financial_item,
            )
            if ObjectiveName.FINANCIALS in [o.name for o in self.objectives]
            else None,
        ).solve(
            weights_tolerance=weights_tolerance,
            created_at=end_date,
        )
        opt_ptf.set_market_data(self.market_data)
        return opt_ptf
