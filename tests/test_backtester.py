"""Test backtester."""

import pandas as pd
import pytest

from optitrader import Optitrader
from optitrader.backtester import Backtester
from optitrader.enums import RebalanceFrequency, UniverseName
from optitrader.optimization.objectives import CVaRObjectiveFunction


@pytest.mark.timeout(0.1)
def test_rebalance_dates(
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test the rebalance dates method."""
    _freq = RebalanceFrequency.MONTHLY
    opt = Optitrader(
        objectives=[CVaRObjectiveFunction()],
        universe_name=UniverseName.POPULAR_STOCKS,
    )
    dates = Backtester(
        opt=opt,
        start=test_start_date,
        rebal_freq=_freq,
        end=test_end_date,
    ).get_rebalance_dates()
    assert isinstance(dates, pd.DatetimeIndex)
    assert len(dates) >= 0
    assert dates.freq.name == _freq.value


@pytest.mark.vcr
def test_compute_history_values(
    test_start_date: pd.Timestamp,
) -> None:
    """Test the compute_history_values method."""
    _freq = RebalanceFrequency.MONTHLY
    opt = Optitrader(
        objectives=[CVaRObjectiveFunction()],
        universe_name=UniverseName.POPULAR_STOCKS,
    )
    test_end_date = test_start_date + pd.Timedelta(days=62)
    backtester = Backtester(
        opt=opt,
        start=test_start_date,
        rebal_freq=_freq,
        end=test_end_date,
    )
    dates = backtester.get_rebalance_dates()
    assert isinstance(dates, pd.DatetimeIndex)
    assert len(dates) == 2  # noqa: PLR2004
    assert dates.freq.name == _freq.value
    history_values = backtester.compute_history_values()
    assert isinstance(history_values, pd.Series)
    assert not history_values.empty
    assert history_values.iloc[0] == 1
