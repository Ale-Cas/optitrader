"""Portfolio module."""

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from alpaca.trading import OrderRequest, OrderSide, OrderType, TimeInForce
from typeguard import typechecked

from optitrader.config import SETTINGS
from optitrader.market import MarketData
from optitrader.models import AssetModel
from optitrader.optimization.objectives import ObjectiveValue


class Portfolio:
    """Portfolio class."""

    @typechecked
    def __init__(
        self,
        weights: pd.Series | dict[str, float],
        objective_values: list[ObjectiveValue] | None = None,
        market_data: MarketData | None = None,
        created_at: pd.Timestamp | None = None,
    ) -> None:
        weights = weights if isinstance(weights, pd.Series) else pd.Series(weights)
        if not weights.empty:
            _wsum = weights.values.sum()
            if _wsum:
                assert (
                    1 - _wsum <= SETTINGS.SUM_WEIGHTS_TOLERANCE
                ), f"The sum of weights has to be 1 not {_wsum}."
        self.weights = pd.Series(weights)
        self.objective_values = objective_values or []
        self.market_data = market_data
        self.created_at = created_at or pd.Timestamp.utcnow()

    def __repr__(self) -> str:
        """Object representation."""
        if self.objective_values:
            objectives_dict = {o.name.value: o.value for o in self.objective_values}
            return f"{self.__class__.__name__}(weights={self.get_non_zero_weights().to_dict()}, objective_values={objectives_dict})"
        return f"{self.__class__.__name__}(weights={self.get_non_zero_weights().to_dict()}"

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
        assets = self.market_data.get_assets(tickers=tuple(weights.keys()))
        assets_in_ptf = []
        for asset in assets:
            asset.weight_in_ptf = weights.get(asset.ticker)
            assets_in_ptf.append(asset)
        return assets_in_ptf

    def get_assets_df(self) -> pd.DataFrame:
        """Return the assets in the portfolio."""
        assert isinstance(
            self.market_data, MarketData
        ), "You must set the market data to get the assets info."
        weights = self.get_non_zero_weights()
        weights.name = "weight_in_ptf"
        assets = self.market_data.get_assets_df(tuple(weights.keys()))
        assets.set_index("ticker", inplace=True)
        return pd.concat([assets, weights], axis=1)

    def get_holdings_df(self) -> pd.DataFrame:
        """Return holdings info df."""
        df = self.get_assets_df()
        if not df.empty:
            return df.sort_values(by="weight_in_ptf", ascending=False)
        return df

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

    def to_orders_list(self, amount: float) -> list[OrderRequest]:
        """Make a list of order requests from the portfolio weights."""
        return [
            OrderRequest(
                symbol=ticker,
                notional=round(weight * amount, 2),
                side=OrderSide.BUY,
                type=OrderType.MARKET,
                time_in_force=TimeInForce.DAY,
            )
            for ticker, weight in self.get_non_zero_weights().sort_values(ascending=False).items()
            if round(weight * amount, 2) >= 1
        ]
