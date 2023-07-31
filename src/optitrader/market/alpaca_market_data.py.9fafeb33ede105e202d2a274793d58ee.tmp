"""Implementation of Alpaca as DataProvider."""

from functools import lru_cache

import pandas as pd
from alpaca.broker import BrokerClient
from alpaca.data import Adjustment, BarSet, StockBarsRequest, StockHistoricalDataClient, TimeFrame
from alpaca.trading import Asset, AssetClass, AssetStatus, GetAssetsRequest, TradingClient
from optitrader.config import SETTINGS
from optitrader.enums import BarsField
from optitrader.market.base_data_provider import BaseDataProvider
from optitrader.market.news import AlpacaNewsAPI, NewsArticle


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
        self.__news_client: AlpacaNewsAPI = AlpacaNewsAPI()

    def get_bars(
        self,
        tickers: tuple[str, ...],
        start_date: pd.Timestamp | None = None,
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
        _last_available_date = pd.Timestamp.utcnow() - pd.Timedelta(15, unit="min")
        _first_available_date = pd.Timestamp("2015-12-12").tz_localize(tz="utc")
        # handle first and last available date from Alpaca
        end_date = (
            end_date
            if end_date and end_date.tz_localize(tz="utc") <= _last_available_date
            else _last_available_date
        )
        start_date = (
            start_date
            if start_date and start_date.tz_localize(tz="utc") >= _first_available_date
            else _first_available_date
        )
        bars = self.__data_client.get_stock_bars(
            StockBarsRequest(
                symbol_or_symbols=sorted(tickers),
                start=start_date,
                end=end_date,
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
        prices.index = prices.index.strftime("%Y-%m-%d")
        return prices.ffill().bfill()

    def get_alpaca_asset(self, ticker: str) -> Asset:
        """Get alpaca asset by ticker."""
        asset = self.__asset_client.get_asset(symbol_or_asset_id=ticker)
        assert isinstance(asset, Asset)
        return asset

    @lru_cache(maxsize=256)  # noqa: B019
    def get_alpaca_assets(
        self,
        status: AssetStatus = AssetStatus.ACTIVE,
        asset_class: AssetClass = AssetClass.US_EQUITY,
        tradable: bool = True,
        marginable: bool = True,
        fractionable: bool = True,
    ) -> list[Asset]:
        """Get alpaca assets."""
        assets = self.__asset_client.get_all_assets(
            GetAssetsRequest(
                status=status,
                asset_class=asset_class,
            )
        )
        assert isinstance(assets, list)
        return [
            a
            for a in assets
            if a.tradable == tradable
            and a.marginable == marginable
            and a.fractionable == fractionable
        ]

    @lru_cache(maxsize=256)  # noqa: B019
    def get_alpaca_tickers(
        self,
        status: AssetStatus = AssetStatus.ACTIVE,
        asset_class: AssetClass = AssetClass.US_EQUITY,
        tradable: bool = True,
        marginable: bool = True,
        fractionable: bool = True,
    ) -> list[str]:
        """Get alpaca asset tickers."""
        return [
            a.symbol
            for a in self.get_alpaca_assets(
                status=status,
                asset_class=asset_class,
                tradable=tradable,
                marginable=marginable,
                fractionable=fractionable,
            )
        ]

    def get_assets_df(
        self,
        status: AssetStatus = AssetStatus.ACTIVE,
        asset_class: AssetClass = AssetClass.US_EQUITY,
        tradable: bool = True,
        marginable: bool = True,
        fractionable: bool = True,
    ) -> pd.DataFrame:
        """Get alpaca assets dataframe."""
        return pd.DataFrame(
            [
                a.dict()
                for a in self.get_alpaca_assets(
                    status=status,
                    asset_class=asset_class,
                    tradable=tradable,
                    marginable=marginable,
                    fractionable=fractionable,
                )
            ]
        )

    @lru_cache  # noqa: B019
    def get_asset_by_name(self, name: str) -> Asset:
        """Get an asset by its name."""
        assets = self.get_alpaca_assets()
        search_result = [a for a in assets if name in str(a.name)][0]
        assert isinstance(search_result, Asset), f"{name} not found."
        return search_result

    def get_news(
        self,
        tickers: tuple[str, ...],
        start: pd.Timestamp | None = None,
        end: pd.Timestamp | None = None,
        limit: int = 5,
        include_content: bool = True,
        exclude_contentless: bool = True,
    ) -> list[NewsArticle]:
        """Get news articles."""
        return self.__news_client.get_news(
            tickers=tickers,
            start=start,
            end=end,
            limit=limit,
            include_content=include_content,
            exclude_contentless=exclude_contentless,
        )

    def get_news_df(
        self,
        tickers: tuple[str, ...],
        start: pd.Timestamp | None = None,
        end: pd.Timestamp | None = None,
        limit: int = 5,
        include_content: bool = True,
        exclude_contentless: bool = True,
    ) -> pd.DataFrame:
        """Get news articles in a df."""
        return self.__news_client.get_news_df(
            tickers=tickers,
            start=start,
            end=end,
            limit=limit,
            include_content=include_content,
            exclude_contentless=exclude_contentless,
        )
