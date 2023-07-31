"""Implementation of Yahoo as DataProvider."""

import logging
from functools import lru_cache

import pandas as pd
from yahooquery import Ticker

from optitrader.enums.market import BalanceSheetItem, BarsField, CashFlowItem, IncomeStatementItem
from optitrader.market.base_data_provider import BaseDataProvider
from optitrader.models.asset import YahooAssetModel

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class YahooMarketData(BaseDataProvider):
    """Class to get market data from Yahoo."""

    def __init__(self) -> None:
        super().__init__()
        self.financials = [
            *IncomeStatementItem.get_values_list(),
            *CashFlowItem.get_values_list(),
            *BalanceSheetItem.get_values_list(),
        ]

    def parse_ticker_for_yahoo(self, ticker: str) -> str:
        """Replace a dot with a hyphen for yahoo in ticker."""
        return ticker.replace(".", "-")

    def parse_ticker_from_yahoo(self, ticker: str) -> str:
        """Replace a dot with a hyphen for yahoo in ticker."""
        return ticker.replace("-", ".")

    def parse_tickers_for_yahoo(self, tickers: tuple[str, ...]) -> tuple[str, ...]:
        """Replace a dot with a hyphen for yahoo in tickers."""
        return tuple(self.parse_ticker_for_yahoo(t) for t in tickers)

    @lru_cache  # noqa: B019
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
        return Ticker(
            symbols=sorted(self.parse_tickers_for_yahoo(tickers)), asynchronous=True
        ).history(start=start_date, end=end_date, adj_ohlc=True)

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

    def get_yahoo_asset(self, ticker: str, fail_on_yf_error: bool = False) -> YahooAssetModel:
        """Get asset info from yahoo."""
        ticker = self.parse_ticker_for_yahoo(ticker)
        try:
            _ticker = Ticker(ticker)
            _profile = _ticker.asset_profile
            if fail_on_yf_error:
                assert isinstance(_profile, dict), f"Yahoo query returned {_profile}"
            elif _profile is None or isinstance(_profile, str):
                # create empty model with None
                return YahooAssetModel()
            elif isinstance(_profile, dict):
                _profile = _ticker.asset_profile[ticker]
            return YahooAssetModel(
                **_profile,
                business_summary=_profile["longBusinessSummary"],
                number_of_shares=_ticker.key_stats[ticker]["sharesOutstanding"],
            )
        except Exception as exc:
            log.debug(f"{ticker}: {type(exc)}")
            if fail_on_yf_error:
                raise AssertionError(f"Yahoo query returned {_profile}") from exc
            return YahooAssetModel()

    def get_number_of_shares(self, ticker: str) -> int:
        """Get the sharesOutstanding field from yahoo query."""
        _shares = Ticker(self.parse_ticker_for_yahoo(ticker)).key_stats[ticker]
        return int(_shares["sharesOutstanding"]) if isinstance(_shares, dict) else 0

    def get_multi_number_of_shares(self, tickers: tuple[str, ...]) -> pd.Series:
        """Get the sharesOutstanding field from yahoo query."""
        tickers = self.parse_tickers_for_yahoo(tickers)
        y_tickers = Ticker(symbols=sorted(tickers), asynchronous=True, max_workers=10)
        return pd.Series(
            {
                self.parse_ticker_from_yahoo(ticker): int(
                    y_tickers.key_stats[ticker]["sharesOutstanding"]
                )
                if isinstance(y_tickers.key_stats[ticker], dict)
                else 0
                for ticker in tickers
            }
        )

    @lru_cache  # noqa: B019
    def get_financials(self, ticker: str) -> pd.DataFrame:
        """Get financials from yahoo finance."""
        ticker = self.parse_ticker_for_yahoo(ticker)
        fin_df = Ticker(ticker).get_financial_data(
            types=self.financials,
            frequency="q",
            trailing=False,
        )
        assert isinstance(fin_df, pd.DataFrame)
        fin_df = fin_df.reset_index().set_index("asOfDate")
        return fin_df[self.financials]

    @lru_cache  # noqa: B019
    def get_multi_financials_by_item(
        self,
        tickers: tuple[str, ...],
        financial_item: IncomeStatementItem
        | CashFlowItem
        | BalanceSheetItem = IncomeStatementItem.NET_INCOME,
    ) -> pd.DataFrame:
        """Get financials from yahoo finance."""
        tickers = self.parse_tickers_for_yahoo(tickers)
        fin_df = Ticker(tickers).get_financial_data(
            types=[financial_item],
            frequency="q",
            trailing=False,
        )
        assert isinstance(fin_df, pd.DataFrame)
        return fin_df.pivot_table(values=financial_item.value, index="asOfDate", columns="symbol")
