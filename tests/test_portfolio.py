"""Test the solver implementation."""
import pandas as pd
import plotly.graph_objs as go
import pytest

from optifolio.config import SETTINGS
from optifolio.market.market_data import MarketData
from optifolio.optimization.constraints import NoShortSellConstraint, SumToOneConstraint
from optifolio.optimization.objectives import (
    CVaRObjectiveFunction,
    MADObjectiveFunction,
    ObjectiveName,
    ObjectiveValue,
)
from optifolio.optimization.solver import Solver
from optifolio.portfolio import Portfolio

_tollerance = SETTINGS.SUM_WEIGHTS_TOLERANCE


def test_portfolio_repr() -> None:
    """Test portfolio representation."""
    test_w = {
        "MSFT": 0.3,
        "TSLA": 0.2,
        "AAPL": 0.5,
    }
    ptf = Portfolio(
        weights=pd.Series(test_w),
        objective_values=[ObjectiveValue(name=ObjectiveName.CVAR, value=0.1, weight=1.0)],
    )
    _rep = repr(ptf)
    assert isinstance(_rep, str)
    assert ptf.__class__.__name__ in _rep
    assert list(test_w.keys())[0] in _rep
    assert ObjectiveName.CVAR.value in _rep


def test_portfolio_set_market_data(
    mock_ptf: Portfolio,
    market_data: MarketData,
) -> None:
    """Set market data method."""
    mock_ptf.set_market_data(market_data)
    assert isinstance(mock_ptf.market_data, MarketData)


def test_portfolio_pie_plot(
    mock_ptf: Portfolio,
) -> None:
    """Test pie_plot method."""
    figure = mock_ptf.pie_plot()
    assert isinstance(figure, go.Figure)


@pytest.mark.vcr()
def test_portfolio_history_plot(
    mock_ptf: Portfolio,
    market_data: MarketData,
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test history_plot method."""
    mock_ptf.set_market_data(market_data)
    assert isinstance(mock_ptf.market_data, MarketData)
    figure = mock_ptf.history_plot(
        start_date=test_start_date,
        end_date=test_end_date,
    )
    assert isinstance(figure, go.Figure)


@pytest.mark.vcr()
def test_portfolio_from_solver(
    market_data: MarketData,
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimal portfolio methods from solver."""
    ptf = Solver(
        returns=market_data.get_total_returns(
            tickers=test_tickers,
            start_date=test_start_date,
            end_date=test_end_date,
        ),
        objectives=[MADObjectiveFunction()],
        constraints=[SumToOneConstraint(), NoShortSellConstraint()],
    ).solve(weights_tolerance=_tollerance)
    weights = ptf.get_non_zero_weights().values
    assert all(weights > _tollerance)
    assert 1 - weights.sum() <= _tollerance
    ptf.set_market_data(market_data)
    history = ptf.get_history(start_date=test_start_date, end_date=test_end_date)
    assert not history.empty


@pytest.mark.vcr()
def test_portfolio_get_holdings_df(
    market_data: MarketData,
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimal portfolio methods from solver."""
    ptf = Solver(
        returns=market_data.get_total_returns(
            tickers=test_tickers,
            start_date=test_start_date,
            end_date=test_end_date,
        ),
        objectives=[CVaRObjectiveFunction()],
        constraints=[SumToOneConstraint(), NoShortSellConstraint()],
    ).solve(weights_tolerance=_tollerance)
    weights = ptf.get_non_zero_weights().values
    assert all(weights > _tollerance)
    assert 1 - weights.sum() <= _tollerance
    ptf.set_market_data(market_data)
    df = ptf.get_holdings_df()
    assert not df.empty
