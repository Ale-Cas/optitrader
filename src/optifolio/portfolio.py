"""Portfolio module."""

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from typeguard import typechecked

from optifolio.config import SETTINGS
from optifolio.market import MarketData
from optifolio.models import AssetModel
from optifolio.optimization.objectives import ObjectiveValue


class Portfolio:
    """Portfolio class."""

    @typechecked
    def __init__(
        self,
        weights: pd.Series | dict[str, float],
        objective_values: list[ObjectiveValue],
        market_data: MarketData | None = None,
        created_at: pd.Timestamp | None = None,
    ) -> None:
        weights = weights if isinstance(weights, pd.Series) else pd.Series(weights)
        _wsum = weights.values.sum()
        assert (
            1 - _wsum <= SETTINGS.SUM_WEIGHTS_TOLERANCE
        ), f"The sum of weights has to be 1 not {_wsum}."
        self.weights = pd.Series(weights)
        self.objective_values = objective_values
        self.market_data = market_data
        self.created_at = created_at

    def __repr__(self) -> str:
        """Object representation."""
        objectives_dict = {o.name.value: o.value for o in self.objective_values}
        return f"{self.__class__.__name__}(weights={self.get_non_zero_weights().to_dict()}, objective_values={objectives_dict})"

    def get_non_zero_weights(self, round_to_decimal: int | None = 5) -> pd.Series:
        """Non zero weights."""
        non_zero = self.weights[self.weights != 0]
        return non_zero.round(round_to_decimal) if round_to_decimal else non_zero

    def get_tickers(self, only_non_zero: bool = True) -> tuple[str, ...]:
        """Get the tickers in portfolio."""
        weights = self.get_non_zero_weights() if only_non_zero else self.weights
        return tuple(weights.keys())

    @typechecked
    def set_market_data(self, market_data: MarketData) -> None:
        """Set the market data."""
        self.market_data = market_data

    def get_assets_in_portfolio(self, only_non_zero: bool = True) -> list[AssetModel]:
        """Return the assets in the portfolio."""
        assert isinstance(
            self.market_data, MarketData
        ), "You must set the market data to get the assets info."
        weights = self.get_non_zero_weights() if only_non_zero else self.weights
        return [
            AssetModel(
                **self.market_data.get_asset_from_ticker(ticker=ticker).dict(
                    exclude={"weight_in_ptf"}
                ),
                weight_in_ptf=weight,
            )
            for ticker, weight in weights.items()
        ]

    def get_holdings_df(self) -> pd.DataFrame:
        """Return holdings info df."""
        return (
            pd.DataFrame(
                [asset.dict() for asset in self.get_assets_in_portfolio()],
            )
            .set_index("symbol")
            .sort_values(by="weight_in_ptf", ascending=False)
        )

    def get_history(
        self,
        start_date: pd.Timestamp,
        end_date: pd.Timestamp | None = None,
    ) -> pd.Series:
        """
        Get the portfolio wealth history.

        Parameters
        ----------
        `start_date`: pd.Timestamp
            The starting date.
        `end_date`: pd.Timestamp
            The ending date. Defaults today.

        Returns
        -------
        `history`: pd.Series
            A timeseries with the portfolio value at each date.
        """
        assert isinstance(
            self.market_data, MarketData
        ), "You must set the market data to get the assets info."
        rets = self.market_data.get_total_returns(
            tickers=self.get_tickers(),
            start_date=start_date,
            end_date=end_date,
        )
        return 1 + (rets * self.get_non_zero_weights()).sum(axis=1, skipna=True).cumsum()

    def pie_plot(self, title: str = "Portfolio Allocation") -> go.Figure:
        """
        Display a pie plot of the weights.

        Parameters
        ----------
        `title`: str
            The title of the plot.
        """
        weights = self.get_non_zero_weights()
        return px.pie(
            data_frame=weights,
            names=weights.keys(),
            values=weights.values,
            title=title,
        )

    def history_plot(
        self,
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        title: str = "Portfolio value from start date to today",
    ) -> go.Figure:
        """
        Display a line plot of the portfolio historical values.

        Parameters
        ----------
        `start_date`: pd.Timestamp
            The starting date. Defaults to a year ago from today.
        `end_date`: pd.Timestamp
            The ending date. Defaults to today.
        `title`: str
            The title of the plot.
        """
        end_date = end_date or pd.Timestamp.today()
        start_date = start_date or end_date - pd.Timedelta(days=365)
        history = self.get_history(start_date=start_date, end_date=end_date)
        return px.line(
            data_frame=history,
            x=history.index,
            y=history.values,
            labels={"timestamp": "", "y": ""},
            title=title,
        )
