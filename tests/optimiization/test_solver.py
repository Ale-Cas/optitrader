"""Test the solver implementation."""
import pandas as pd
import vcr

from optifolio.market.market_data import MarketData
from optifolio.optimization.constraints import NoShortSellConstraint, SumToOneConstraint
from optifolio.optimization.objectives import CVaRObjectiveFunction, MADObjectiveFunction
from optifolio.optimization.solver import Solver


@vcr.use_cassette("tests/data/cassettes/test_get_bars.yaml")
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
        objective_functions=[CVaRObjectiveFunction()],
        constraint_functions=[SumToOneConstraint(), NoShortSellConstraint()],
    ).solve()
    assert all(sol.weights.values >= 0)
    assert 1 - sum(sol.weights) <= _tollerance


@vcr.use_cassette("tests/data/cassettes/test_get_bars.yaml")
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
            objective_functions=[MADObjectiveFunction()],
            constraint_functions=[SumToOneConstraint(), NoShortSellConstraint()],
        )
        .solve(weights_tolerance=_tollerance)
        .get_non_zero_weights()
    )
    assert all(weights.values > _tollerance)
    assert 1 - sum(weights) <= _tollerance
