"""Portfolio module."""
import pandas as pd

from optifolio.optimization.objectives import ObjectiveValue


class Portfolio:
    """Portfolio class."""

    def __init__(
        self,
        weights: pd.Series,
        objective_values: list[ObjectiveValue],
    ) -> None:
        self.weights = weights
        self.objective_values = objective_values

    def get_non_zero_weights(self) -> pd.Series:
        """Non zero weights."""
        return self.weights[self.weights != 0]

    # TODO: compute a dataframe of holding informations
    def get_holdings_df(self) -> pd.DataFrame:
        """Return holdings info df."""
