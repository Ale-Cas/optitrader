"""Portfolio module."""
import pandas as pd
from typeguard import typechecked

from optifolio.market import MarketData
from optifolio.models import AssetModel
from optifolio.optimization.objectives import ObjectiveValue


class Portfolio:
    """Portfolio class."""

    def __init__(
        self,
        weights: pd.Series,
        objective_values: list[ObjectiveValue],
        market_data: MarketData | None = None,
    ) -> None:
        self.weights = weights
        self.objective_values = objective_values
        self.market_data = market_data

    def get_non_zero_weights(self) -> pd.Series:
        """Non zero weights."""
        return self.weights[self.weights != 0]

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
        return pd.DataFrame(
            [asset.dict() for asset in self.get_assets_in_portfolio()],
        ).set_index("symbol")
