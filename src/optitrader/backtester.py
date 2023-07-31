"""Backtester implementation."""

import pandas as pd
import streamlit as st

from optitrader import Optitrader, Portfolio
from optitrader.enums import RebalanceFrequency
from optitrader.utils import rearrange_columns_by_zeros


class Portfolios:
    """Container of Portfolio objects."""

    def __init__(self, ptfs: list[Portfolio]) -> None:
        """Portfolio init."""
        self.ptfs = ptfs

    def to_df(self) -> pd.DataFrame:
        """To dataframe of weights at each date."""
        _df = pd.DataFrame({p.created_at: p.weights for p in self.ptfs}).T
        _df.index = _df.index.strftime("%Y-%m-%d")
        return rearrange_columns_by_zeros(_df)


class Backtester:
    """Backtester class."""

    def __init__(
        self,
        opt: Optitrader,
        rebal_freq: RebalanceFrequency = RebalanceFrequency.MONTHLY,
        end: pd.Timestamp | None = None,
        start: pd.Timestamp | None = None,
    ) -> None:
        """Initialize new backtester instance."""
        self.opt = opt
        self.rebal_freq = rebal_freq
        self.end = end or pd.Timestamp.today().normalize()
        self.start = start or (self.end - pd.Timedelta(days=365 * 2)).normalize()
        self.ptfs: list[Portfolio] = []

    def get_rebalance_dates(self) -> pd.DatetimeIndex:
        """Return the list of rebalance dates."""
        return pd.date_range(
            start=self.start,
            end=self.end,
            freq=self.rebal_freq.value,
            normalize=True,
        )

    def compute_portfolios(
        self,
        progress_bar: bool = True,
    ) -> list[Portfolio]:
        """Compute portfolio solutions."""
        dates = self.get_rebalance_dates()
        if progress_bar:
            bar = st.progress(0, "Backtest in progress. Please wait.")
        for idx, date in enumerate(dates):
            bar.progress((idx + 1) / len(dates), f"Computing optimal portfolio on {date.date()!s}")
            try:
                self.ptfs.append(self.opt.solve(end_date=date))
            except Exception as e:
                bar.error(e)
                raise e from e
        bar.empty()
        return self.ptfs

    def compute_history_values(self) -> pd.Series:
        """Compute the strategy wealth in the history."""
        rets = self.opt.market_data.get_total_returns(
            tickers=self.opt.investment_universe.tickers,
            start_date=self.start,
            end_date=self.end,
        )
        ptfs = Portfolios(self.ptfs or self.compute_portfolios()).to_df()
        return 1 + (rets * ptfs.reindex(rets.index, method="ffill").fillna(0)).sum(axis=1).cumsum()
