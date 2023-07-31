"""Module with data provider base class."""

from typing import Protocol

import pandas as pd

from optitrader.enums import BarsField


class BaseDataProvider(Protocol):
    """Abstract base class for a data provider."""

    def __init__(self) -> None:
        super().__init__()

    def get_bars(
        self,
        tickers: tuple[str, ...],
        start_date: pd.Timestamp,
        end_date: pd.Timestamp | None = None,
    ) -> pd.DataFrame:
        """Get bars from the data provider."""

    def get_prices(
        self,
        tickers: tuple[str, ...],
        start_date: pd.Timestamp,
        end_date: pd.Timestamp | None = None,
        bars_field: BarsField = BarsField.CLOSE,
    ) -> pd.DataFrame:
        """Get prices from the data provider."""
