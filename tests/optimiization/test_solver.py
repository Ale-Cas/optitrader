"""Test the solver implementation."""
import pandas as pd
import pytest
import vcr

from optifolio.enums.market import UniverseName
from optifolio.market.investment_universe import InvestmentUniverse
from optifolio.market.market_data import MarketData
from optifolio.optimization.constraints import (
    NoShortSellConstraint,
    NumberOfAssetsConstraint,
    SumToOneConstraint,
    WeightsConstraint,
)
from optifolio.optimization.objectives import CVaRObjectiveFunction, MADObjectiveFunction
from optifolio.optimization.solver import Solver


@vcr.use_cassette("tests/data/cassettes/test_load_prices.yaml")
def test_solver_cvar(
    market_data: MarketData,
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimization solver."""
    _tollerance = 1e-4
    sol = Solver(
        returns=market_data.get_total_returns(
            tickers=test_tickers,
            start_date=test_start_date,
            end_date=test_end_date,
        ),
        objectives=[CVaRObjectiveFunction()],
        constraints=[SumToOneConstraint(), NoShortSellConstraint()],
    ).solve()
    assert all(sol.weights.values >= 0)
    assert 1 - sum(sol.weights) <= _tollerance


@vcr.use_cassette("tests/data/cassettes/test_load_prices.yaml")
def test_solver_mad(
    market_data: MarketData,
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimization solver."""
    _tollerance = 1e-2
    weights = (
        Solver(
            returns=market_data.get_total_returns(
                tickers=test_tickers,
                start_date=test_start_date,
                end_date=test_end_date,
            ),
            objectives=[MADObjectiveFunction()],
            constraints=[SumToOneConstraint(), NoShortSellConstraint()],
        )
        .solve(weights_tolerance=_tollerance)
        .get_non_zero_weights()
    )
    assert all(weights.values > _tollerance)
    assert 1 - sum(weights) <= _tollerance


@pytest.mark.vcr()
def test_solver_min_num_assets(
    market_data: MarketData,
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimization solver."""
    _tollerance = 1e-2
    _min = 7
    weights = (
        Solver(
            returns=market_data.get_total_returns(
                tickers=InvestmentUniverse(name=UniverseName.POPULAR_STOCKS).tickers,
                start_date=test_start_date,
                end_date=test_end_date,
            ),
            objectives=[MADObjectiveFunction()],
            constraints=[
                SumToOneConstraint(),
                NoShortSellConstraint(),
                NumberOfAssetsConstraint(
                    lower_bound=_min,
                ),
            ],
        )
        .solve(weights_tolerance=_tollerance)
        .get_non_zero_weights()
    )
    assert len(weights.index) >= _min
    assert all(weights.values > _tollerance)
    assert 1 - sum(weights) <= _tollerance


@vcr.use_cassette("tests/data/cassettes/test_solver_min_num_assets.yaml")
def test_solver_max_num_assets(
    market_data: MarketData,
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimization solver."""
    _tollerance = 1e-2
    _max = 7
    weights = (
        Solver(
            returns=market_data.get_total_returns(
                tickers=InvestmentUniverse(name=UniverseName.POPULAR_STOCKS).tickers,
                start_date=test_start_date,
                end_date=test_end_date,
            ),
            objectives=[MADObjectiveFunction()],
            constraints=[
                SumToOneConstraint(),
                NoShortSellConstraint(),
                NumberOfAssetsConstraint(
                    upper_bound=_max,
                ),
            ],
        )
        .solve(weights_tolerance=_tollerance)
        .get_non_zero_weights()
    )
    assert len(weights.index) <= _max
    assert all(weights.values > _tollerance)
    assert 1 - sum(weights) <= _tollerance


@vcr.use_cassette("tests/data/cassettes/test_solver_min_num_assets.yaml")
def test_solver_exact_num_assets(
    market_data: MarketData,
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimization solver."""
    _tollerance = 1e-2
    _num = 7
    weights = (
        Solver(
            returns=market_data.get_total_returns(
                tickers=InvestmentUniverse(name=UniverseName.POPULAR_STOCKS).tickers,
                start_date=test_start_date,
                end_date=test_end_date,
            ),
            objectives=[MADObjectiveFunction()],
            constraints=[
                SumToOneConstraint(),
                NoShortSellConstraint(),
                NumberOfAssetsConstraint(
                    lower_bound=_num,
                    upper_bound=_num,
                ),
            ],
        )
        .solve(weights_tolerance=_tollerance)
        .get_non_zero_weights()
    )
    assert len(weights.index) == _num
    assert all(weights.values > _tollerance)
    assert 1 - sum(weights) <= _tollerance


@vcr.use_cassette("tests/data/cassettes/test_solver_min_num_assets.yaml")
def test_solver_min_weight(
    market_data: MarketData,
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimization solver."""
    _tollerance = 1e-2
    tickers = InvestmentUniverse(name=UniverseName.POPULAR_STOCKS).tickers
    _num = int(100 / len(tickers))
    weights = (
        Solver(
            returns=market_data.get_total_returns(
                tickers=InvestmentUniverse(name=UniverseName.POPULAR_STOCKS).tickers,
                start_date=test_start_date,
                end_date=test_end_date,
            ),
            objectives=[MADObjectiveFunction()],
            constraints=[
                SumToOneConstraint(),
                NoShortSellConstraint(),
                WeightsConstraint(
                    lower_bound=_num,
                ),
            ],
        )
        .solve(weights_tolerance=_tollerance)
        .get_non_zero_weights()
    )
    assert weights.min() >= _num / 100
    assert all(weights.values >= _num / 100)
    assert 1 - sum(weights) <= _tollerance
