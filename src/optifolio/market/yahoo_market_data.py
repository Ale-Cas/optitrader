"""Implementation of Alpaca as DataProvider."""

import pandas as pd
from yahooquery import Ticker

from optifolio.market.base_data_provider import BaseDataProvider
from optifolio.market.enums import BarsField


class YahooMarketData(BaseDataProvider):
    """Class to get market data from Alpaca."""

    def __init__(self) -> None:
        super().__init__()

    def get_bars(
        self,
        tickers: tuple[str, ...],
        start_date: pd.Timestamp,
        end_date: pd.Timestamp | None = None,
    ) -> pd.DataFrame:
        """
        Get the daily bars dataframe from alpaca-py historical client.

        Parameters
        ----------
        `tickers`: tuple[str, ...]
            A tuple of str representing the tickers.
        `start_date`: pd.Timestamp
            A pd.Timestamp representing start date.
        `end_date`: pd.Timestamp
            A pd.Timestamp representing end date.

        Returns
        -------
        `bars`
            a pd.DataFrame with the bars for the tickers.
        """
        return Ticker(symbols=sorted(tickers), asynchronous=True).history(
            start=start_date, end=end_date, adj_ohlc=True
        )

    def get_prices(
        self,
        tickers: tuple[str, ...],
        start_date: pd.Timestamp,
        end_date: pd.Timestamp | None = None,
        bars_field: BarsField = BarsField.CLOSE,
    ) -> pd.DataFrame:
        """
        Get the daily bars dataframe from alpaca-py historical client.

        Parameters
        ----------
        `tickers`: tuple[str, ...]
            A tuple of str representing the tickers.
        `start_date`: pd.Timestamp
            A pd.Timestamp representing start date.
        `end_date`: pd.Timestamp
            A pd.Timestamp representing end date.

        Returns
        -------
        `bars`
            a pd.DataFrame with the bars for the tickers.
        """
        bars = self.get_bars(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
        )
        bars.reset_index(inplace=True)
        _index_name = "date"
        return bars.pivot(index=_index_name, columns="symbol", values=bars_field)
