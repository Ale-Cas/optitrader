"""Test the solver implementation."""
import pandas as pd
import pytest
import vcr

from optitrader.config import SETTINGS
from optitrader.enums.market import UniverseName
from optitrader.market.investment_universe import InvestmentUniverse
from optitrader.market.market_data import MarketData
from optitrader.optimization.constraints import (
    NoShortSellConstraint,
    NumberOfAssetsConstraint,
    SumToOneConstraint,
    WeightsConstraint,
)
from optitrader.optimization.objectives import (
    CovarianceObjectiveFunction,
    CVaRObjectiveFunction,
    FinancialsObjectiveFunction,
    MADObjectiveFunction,
    MostDiversifiedObjectiveFunction,
)
from optitrader.optimization.solver import Solver

_tollerance = SETTINGS.SUM_WEIGHTS_TOLERANCE


@vcr.use_cassette("tests/data/cassettes/test_load_prices.yaml")
def test_solver_cvar(
    market_data: MarketData,
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimization solver."""
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
def test_solver_covariance(
    market_data: MarketData,
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimization solver."""
    sol = Solver(
        returns=market_data.get_total_returns(
            tickers=test_tickers,
            start_date=test_start_date,
            end_date=test_end_date,
        ),
        objectives=[CovarianceObjectiveFunction()],
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


@vcr.use_cassette("tests/data/cassettes/test_load_prices.yaml")
def test_solver_mdp(
    market_data: MarketData,
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimization solver."""
    weights = (
        Solver(
            returns=market_data.get_total_returns(
                tickers=test_tickers,
                start_date=test_start_date,
                end_date=test_end_date,
            ),
            objectives=[MostDiversifiedObjectiveFunction()],
            constraints=[SumToOneConstraint(), NoShortSellConstraint()],
        )
        .solve(weights_tolerance=_tollerance)
        .get_non_zero_weights()
    )
    assert all(weights.values > _tollerance)
    assert 1 - sum(weights) <= _tollerance


@pytest.mark.vcr(match_on=["method", "scheme", "host", "port", "path"])
@pytest.mark.skip(reason="Yahoo finance returns empty dataframe")
def test_solver_financials(
    market_data: MarketData,
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimization solver."""
    financials_df = market_data.get_multi_financials_by_item(
        tickers=test_tickers,
    )
    solver = Solver(
        returns=market_data.get_total_returns(
            tickers=test_tickers,
            start_date=test_start_date,
            end_date=test_end_date,
        ),
        objectives=[
            FinancialsObjectiveFunction(
                weight=0.3,
            ),
        ],
        financials_df=financials_df,
        constraints=[SumToOneConstraint(), NoShortSellConstraint()],
    )
    assert len(solver.returns.index)
    weights = solver.solve(weights_tolerance=_tollerance).get_non_zero_weights()
    assert all(weights.values > _tollerance)
    assert 1 - sum(weights) <= _tollerance
    assert len(weights.values) > 0
    assert isinstance(solver.financials_df, pd.DataFrame)
    assert solver.financials_df.sum(axis=1).idxmax() == sorted(weights.keys())[0]


@pytest.mark.vcr(match_on=["method", "scheme", "host", "port", "path"])
@pytest.mark.skip(reason="Yahoo finance returns empty dataframe")
def test_solver_financials_and_cvar(
    market_data: MarketData,
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimization solver."""
    test_tickers = InvestmentUniverse(name=UniverseName.NASDAQ).tickers
    weights_tolerance = 1e-4
    weights = (
        Solver(
            returns=market_data.get_total_returns(
                tickers=test_tickers,
                start_date=test_start_date,
                end_date=test_end_date,
            ),
            objectives=[
                CVaRObjectiveFunction(),
                FinancialsObjectiveFunction(
                    weight=0.1,
                ),
            ],
            financials_df=market_data.get_multi_financials_by_item(
                tickers=test_tickers,
            ),
            constraints=[SumToOneConstraint(), NoShortSellConstraint()],
        )
        .solve(weights_tolerance=weights_tolerance)
        .get_non_zero_weights()
    )
    assert all(weights.values > weights_tolerance)
    assert 1 - sum(weights) <= _tollerance
    assert len(weights.values) > 1


@pytest.mark.vcr()
def test_solver_min_num_assets(
    market_data: MarketData,
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test optimization solver."""
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
