"""Module to handle market data."""

import asyncio
import logging
import time
from functools import lru_cache

import finnhub
import pandas as pd
from optitrader.config import SETTINGS
from optitrader.enums import BarsField, DataProvider
from optitrader.enums.market import BalanceSheetItem, CashFlowItem, IncomeStatementItem
from optitrader.market.alpaca_market_data import AlpacaMarketData, Asset
from optitrader.market.base_data_provider import BaseDataProvider
from optitrader.market.db.database import MarketDB
from optitrader.market.finnhub_market_data import FinnhubClient
from optitrader.market.news import NewsArticle
from optitrader.market.yahoo_market_data import YahooMarketData
from optitrader.models.asset import AssetModel, _YahooFinnhubCommon

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class MarketData:
    """Class that implements market data connections."""

    def __init__(
        self,
        data_provider: DataProvider = DataProvider.ALPACA,
        trading_key: str | None = SETTINGS.ALPACA_TRADING_API_KEY,
        trading_secret: str | None = SETTINGS.ALPACA_TRADING_API_SECRET,
        broker_key: str | None = SETTINGS.ALPACA_BROKER_API_KEY,
        broker_secret: str | None = SETTINGS.ALPACA_BROKER_API_SECRET,
        use_db: bool = True,
    ) -> None:
        self._trading_key = trading_key
        self._trading_secret = trading_secret
        self._broker_key = broker_key
        self._broker_secret = broker_secret
        self.__alpaca_client = AlpacaMarketData(
            trading_key=trading_key,
            trading_secret=trading_secret,
            broker_key=broker_key,
            broker_secret=broker_secret,
        )
        self.__yahoo_client = YahooMarketData()
        self.__finnhub = FinnhubClient()
        provider_mapping: dict[DataProvider, BaseDataProvider] = {
            DataProvider.ALPACA: self.__alpaca_client,
            DataProvider.YAHOO: self.__yahoo_client,
        }
        self.__provider_client = provider_mapping[data_provider]
        self.use_db = use_db
        if self.use_db:
            self._db = MarketDB()

    @lru_cache  # noqa: B019
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

    def get_asset(self, ticker: str) -> AssetModel:
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
        if self.use_db:
            return self._db.get_asset(ticker)
        return self.get_asset_from_ticker(ticker)

    @lru_cache  # noqa: B019
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
        duplicate_fields = set(_YahooFinnhubCommon.__fields__.keys())
        apca_asset = self.__alpaca_client.get_alpaca_asset(ticker)
        finnhub_asset = self.__finnhub.get_asset_profile(ticker)
        yahoo_asset = self.__yahoo_client.get_yahoo_asset(ticker)
        return AssetModel(
            **apca_asset.dict(exclude_none=True),
            **yahoo_asset.dict(
                exclude=duplicate_fields,
                exclude_none=True,
            )
            if yahoo_asset
            else {},
            **finnhub_asset.dict(
                exclude=duplicate_fields,
                exclude_none=True,
            )
            if finnhub_asset
            else {},
        )

    def _get_asset_from_ticker(self, ticker: str) -> AssetModel | None:
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
        try:
            return self.get_asset_from_ticker(ticker)
        except Exception as error:
            log.debug(ticker)
            log.debug(type(error))
            return None

    async def _async_get_assets(self, tickers: tuple[str, ...]) -> list[AssetModel]:
        """
        Return assets info from ticker.

        Parameters
        ----------
        `tickers`: tuple(str)
            A tuple of str representing the tickers.

        Returns
        -------
        `assets`
            A list of AssetModel data model.
        """
        _threads = [asyncio.to_thread(self._get_asset_from_ticker, ticker) for ticker in tickers]
        return await asyncio.gather(*_threads)

    @lru_cache  # noqa: B019
    def get_assets_from_provider(self, tickers: tuple[str, ...]) -> list[AssetModel]:
        """
        Return assets info from ticker.

        Parameters
        ----------
        `tickers`: tuple(str)
            A tuple of str representing the tickers.

        Returns
        -------
        `assets`
            A list of AssetModel data model.
        """
        tickers_bucket_size = 30
        assets = []
        start = time.time()
        for i in range(0, len(tickers), tickers_bucket_size):
            tickers_bucket = tickers[i : i + tickers_bucket_size]
            try:
                _new_assets = asyncio.run(self._async_get_assets(tickers=tickers_bucket))
            except finnhub.FinnhubAPIException as api_error:
                reset_remaining = 60 - (time.time() - start)
                log.warning(f"Request for tickers {tickers_bucket} sleeping {reset_remaining}")
                log.warning(type(api_error))
                if reset_remaining:
                    time.sleep(reset_remaining)  # wait time limit reset
                _new_assets = asyncio.run(self._async_get_assets(tickers=tickers_bucket))
            assets.extend([a for a in _new_assets if a is not None])
        return assets

    def get_assets(self, tickers: tuple[str, ...] | None = None) -> list[AssetModel]:
        """
        Return assets info from tickers.

        If self.use_db it returns from the database,
        otherwise from the data provider.

        Parameters
        ----------
        `tickers`: tuple(str)
            A tuple of str representing the tickers.

        Returns
        -------
        `assets`
            A list of AssetModel data model.
        """
        if self.use_db:
            return self._db.get_asset_models(tickers)
        assert tickers, "Use the tickers or set use_db = True"
        return self.get_assets_from_provider(tickers)

    def get_assets_df(
        self,
        tickers: tuple[str, ...] | None = None,
    ) -> pd.DataFrame:
        """
        Return assets info from ticker.

        Parameters
        ----------
        `tickers`: tuple(str)
            A tuple of str representing the tickers.

        Returns
        -------
        `assets`
            A list of AssetModel data model.
        """
        if self.use_db:
            return self._db.get_assets_df(tickers)
        return pd.DataFrame([a.dict() for a in self.get_assets(tickers)])

    @lru_cache  # noqa: B019
    def get_financials(self, ticker: str) -> pd.DataFrame:
        """
        Return asset info from ticker.

        Parameters
        ----------
        `ticker`: str
            A str representing the ticker.

        Returns
        -------
        `fin_df`
            pd.DataFrame of financials.
        """
        return self.__yahoo_client.get_financials(ticker)

    @lru_cache  # noqa: B019
    def get_multi_financials_by_item(
        self,
        tickers: tuple[str, ...],
        financial_item: IncomeStatementItem
        | CashFlowItem
        | BalanceSheetItem = IncomeStatementItem.NET_INCOME,
    ) -> pd.DataFrame:
        """
        Return asset info from tickers.

        Parameters
        ----------
        `tickers`: str
            A str representing the tickers.
        `financial_item`: IncomeStatementItem
        | CashFlowItem
        | BalanceSheetItem = IncomeStatementItem.NET_INCOME

        Returns
        -------
        `fin_df`
            pd.DataFrame of financials.
        """
        return self.__yahoo_client.get_multi_financials_by_item(
            tickers, financial_item=financial_item
        )

    def get_tradable_tickers(self) -> tuple[str, ...]:
        """Get all tradable tickers from Alpaca."""
        return tuple(self.__alpaca_client.get_alpaca_tickers())

    def get_asset_by_name(self, name: str) -> Asset:
        """Get asset by name from Alpaca."""
        return self.__alpaca_client.get_asset_by_name(name)

    def get_total_number_of_shares(
        self,
        tickers: tuple[str, ...],
    ) -> pd.Series:
        """Get the number of shares for each ticket in tickets."""
        if self.use_db:
            return self._db.get_number_of_shares(tickers).set_index("ticker")
        return self.__yahoo_client.get_multi_number_of_shares(tickers)

    def get_market_caps(
        self,
        tickers: tuple[str, ...],
        start_date: pd.Timestamp,
        end_date: pd.Timestamp | None = None,
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
        return self.load_prices(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
        ).mul(self.get_total_number_of_shares(tickers)["number_of_shares"], axis=1)

    def get_top_market_caps(
        self,
        tickers: tuple[str, ...],
        top: int,
    ) -> pd.Series:
        """Get the tickers with the top market cap."""
        caps = self.get_market_caps(
            tickers=tickers,
            # only taking last week data for the market cap
            start_date=pd.Timestamp.today() - pd.Timedelta(days=5),
        )
        return caps.iloc[-1, :].sort_values(ascending=False)[:top]

    def get_top_market_cap_tickers(
        self,
        tickers: tuple[str, ...],
        top: int = 10,
    ) -> tuple[str, ...]:
        """Get the tickers with the top market cap."""
        return tuple(self.get_top_market_caps(tickers=tickers, top=top).index)

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
        return self.__alpaca_client.get_news(
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
        return self.__alpaca_client.get_news_df(
            tickers=tickers,
            start=start,
            end=end,
            limit=limit,
            include_content=include_content,
            exclude_contentless=exclude_contentless,
        )
