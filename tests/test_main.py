"""Test the Optifolio class implementation."""
import pandas as pd
import pytest
import vcr
from alpaca.common import APIError

from optifolio import Optifolio
from optifolio.enums import UniverseName
from optifolio.market import MarketData
from optifolio.optimization.objectives import (
    CVaRObjectiveFunction,
    ExpectedReturnsObjectiveFunction,
)


@pytest.mark.vcr()
def test_optifolio_cvar_universe(
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimal portfolio."""
    _tollerance = 1e-3
    opt_ptf = Optifolio(
        objectives=[CVaRObjectiveFunction()], universe_name=UniverseName.POPULAR_STOCKS
    ).solve(
        start_date=test_start_date,
        end_date=test_end_date,
    )
    weights = opt_ptf.get_non_zero_weights().values
    assert all(weights > _tollerance)
    assert 1 - weights.sum() <= _tollerance


@pytest.mark.vcr()
def test_optifolio_cvar_tickers(
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimal portfolio."""
    _tollerance = 1e-3
    opt_ptf = Optifolio(objectives=[CVaRObjectiveFunction()], tickers=test_tickers).solve(
        start_date=test_start_date,
        end_date=test_end_date,
    )
    weights = opt_ptf.get_non_zero_weights().values
    assert all(weights > _tollerance)
    assert 1 - weights.sum() <= _tollerance


@vcr.use_cassette("tests/cassettes/test_optifolio_cvar.yaml")
def test_optifolio_custom_market_data(
    market_data: MarketData,
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimal portfolio."""
    _tollerance = 1e-3
    opt_ptf = Optifolio(
        objectives=[ExpectedReturnsObjectiveFunction()],
        tickers=test_tickers,
        market_data=market_data,
    ).solve(
        start_date=test_start_date,
        end_date=test_end_date,
    )
    weights = opt_ptf.get_non_zero_weights().values
    assert all(weights > _tollerance)
    assert 1 - weights.sum() <= _tollerance


def test_optifolio_invalid_market_data(
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimal portfolio."""
    with pytest.raises(expected_exception=APIError, match="forbidden"):
        Optifolio(
            objectives=[ExpectedReturnsObjectiveFunction()],
            tickers=test_tickers,
            market_data=MarketData(trading_key="invalid"),
        ).solve(
            start_date=test_start_date,
            end_date=test_end_date,
        )
