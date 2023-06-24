"""Module to handle market data."""

import pandas as pd

from optifolio.market.alpaca_market_data import AlpacaMarketData
from optifolio.market.base_data_provider import BaseDataProvider
from optifolio.market.enums import BarsField, DataProvider
from optifolio.market.yahoo_market_data import YahooMarketData
from optifolio.models.asset import AssetModel


class MarketData:
    """Class that implements market data connections."""

    def __init__(
        self,
        data_provider: DataProvider = DataProvider.ALPACA,
    ) -> None:
        self.__alpaca_client = AlpacaMarketData()
        self.__yahoo_client = YahooMarketData()
        provider_mapping: dict[DataProvider, BaseDataProvider] = {
            DataProvider.ALPACA: self.__alpaca_client,
            DataProvider.YAHOO: self.__yahoo_client,
        }
        self.__provider_client = provider_mapping[data_provider]

    def load_prices(
        self,
        tickers: tuple[str, ...],
        start_date: pd.Timestamp,
        end_date: pd.Timestamp | None = None,
        bars_field: BarsField = BarsField.CLOSE,
    ) -> pd.DataFrame:
        """
        Load the prices df from the data provider.

        Parameters
        ----------
        `tickers`: tuple[str, ...]
            A tuple of str representing the tickers.
        `start_date`: pd.Timestamp
            A pd.Timestamp representing start date.
        `end_date`: pd.Timestamp
            A pd.Timestamp representing end date.
        `bars_field`: BarsField
            A field in the OHLCV bars. Defaults to CLOSE.
        `excel_filename` str | None
            The path for an excel file with custom prices.
            Defaults to None and is required only if the DataProvider is EXCEL_FILE.

        Returns
        -------
        `prices`
            pd.DataFrame with market prices.
        """
        return self.__provider_client.get_prices(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            bars_field=bars_field,
        )

    def get_total_returns(
        self,
        tickers: tuple[str, ...],
        start_date: pd.Timestamp,
        end_date: pd.Timestamp | None = None,
        required_pct_obs: float = 0.95,
    ) -> pd.DataFrame:
        """
        Return total return dataframe.

        Parameters
        ----------
        `tickers`: tuple[str, ...]
            A tuple of str representing the tickers.
        `start_date`: pd.Timestamp
            A pd.Timestamp representing start date.
        `end_date`: pd.Timestamp
            A pd.Timestamp representing end date.
        `required_pct_obs`: float
            Minimum treshold for non NaNs in each column.
            Columns with more NaNs(%)>required_pct_obs will be dropped.

        Returns
        -------
        `returns`
            pd.DataFrame with market linear returns.
        """
        returns = (
            self.load_prices(
                tickers=tickers,
                start_date=start_date,
                end_date=end_date,
            )
            .pct_change()
            .iloc[1:, :]
        )
        # remove tickers that do not have enough observations
        return returns.dropna(axis=1, thresh=int(returns.shape[0] * required_pct_obs))

    def get_asset_from_ticker(self, ticker: str) -> AssetModel:
        """
        Return asset info from ticker.

        Parameters
        ----------
        `ticker`: str
            A str representing the ticker.

        Returns
        -------
        `asset`
            AssetModel data model.
        """
        apca_asset = self.__alpaca_client.get_alpaca_asset(ticker)
        yahoo_asset = self.__yahoo_client.get_yahoo_asset(ticker)
        return AssetModel(
            **apca_asset.dict(),
            **yahoo_asset.dict(),
        )
