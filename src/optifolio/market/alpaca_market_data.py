"""Implementation of Alpaca as DataProvider."""

import pandas as pd
from alpaca.broker import BrokerClient
from alpaca.data import Adjustment, BarSet, StockBarsRequest, StockHistoricalDataClient, TimeFrame
from alpaca.trading import Asset, AssetClass, AssetStatus, GetAssetsRequest, TradingClient

from optifolio.config import SETTINGS
from optifolio.market.base_data_provider import BaseDataProvider
from optifolio.market.enums import BarsField


class AlpacaMarketData(BaseDataProvider):
    """Class to get market data from Alpaca."""

    def __init__(
        self,
        trading_key: str | None = SETTINGS.ALPACA_TRADING_API_KEY,
        trading_secret: str | None = SETTINGS.ALPACA_TRADING_API_SECRET,
        broker_key: str | None = SETTINGS.ALPACA_BROKER_API_KEY,
        broker_secret: str | None = SETTINGS.ALPACA_BROKER_API_SECRET,
    ) -> None:
        super().__init__()
        assert (
            SETTINGS.is_trading or SETTINGS.is_broker
        ), "Either Trading API or Broker API keys must be provided to use this service."
        self.__data_client = (
            StockHistoricalDataClient(
                api_key=trading_key,
                secret_key=trading_secret,
            )
            if SETTINGS.is_trading
            else StockHistoricalDataClient(
                api_key=broker_key,
                secret_key=broker_secret,
                use_basic_auth=True,
            )
        )
        self.__asset_client: BrokerClient | TradingClient = (
            TradingClient(
                api_key=trading_key,
                secret_key=trading_secret,
            )
            if SETTINGS.is_trading
            else BrokerClient(
                api_key=broker_key,
                secret_key=broker_secret,
            )
        )

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
        bars = self.__data_client.get_stock_bars(
            StockBarsRequest(
                symbol_or_symbols=sorted(tickers),
                start=start_date,
                end=end_date + pd.Timedelta(5, unit="hours"),  # needed to include last day
                adjustment=Adjustment.ALL,
                timeframe=TimeFrame.Day,
            )
        )
        assert isinstance(bars, BarSet)
        return bars.df

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
        _index_name = "timestamp"
        prices = bars.pivot(index=_index_name, columns="symbol", values=bars_field)
        prices.index = pd.to_datetime(prices.index, format="%Y-%m-%d")
        return prices

    def get_alpaca_asset(self, ticker: str) -> Asset:
        """Get alpaca asset by ticker."""
        asset = self.__asset_client.get_asset(symbol_or_asset_id=ticker)
        assert isinstance(asset, Asset)
        return asset

    def get_alpaca_assets(
        self,
        status: AssetStatus = AssetStatus.ACTIVE,
        asset_class: AssetClass = AssetClass.US_EQUITY,
    ) -> list[Asset]:
        """Get alpaca asset by ticker."""
        assets = self.__asset_client.get_all_assets(
            GetAssetsRequest(
                status=status,
                asset_class=asset_class,
            )
        )
        assert isinstance(assets, list)
        return assets
