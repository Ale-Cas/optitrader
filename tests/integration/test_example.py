"""Test the example code in the documentation."""

import pandas as pd
import pytest

from optitrader import Optitrader
from optitrader.config import SETTINGS
from optitrader.enums import UniverseName
from optitrader.optimization.objectives import CVaRObjectiveFunction, ObjectiveName

_tollerance = SETTINGS.SUM_WEIGHTS_TOLERANCE


@pytest.mark.timeout(30)
@pytest.mark.vcr(match_on=["method", "scheme", "host", "port", "path"])
def test_optitrader_example_readme() -> None:
    """Test readme example."""
    optimal_ptf = Optitrader(
        objectives=[CVaRObjectiveFunction()],
        universe_name=UniverseName.POPULAR_STOCKS,
    ).solve()
    assert 1 - optimal_ptf.weights.values.sum() <= _tollerance
    assert optimal_ptf.objective_values[0].name == ObjectiveName.CVAR


@pytest.mark.timeout(10)
@pytest.mark.vcr()
def test_optitrader_example_faang(
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test the same example on less stocks."""
    optimal_ptf = Optitrader(
        objectives=[CVaRObjectiveFunction()],
        universe_name=UniverseName.FAANG,
    ).solve(start_date=test_start_date, end_date=test_end_date)
    assert 1 - optimal_ptf.weights.values.sum() <= _tollerance
    assert optimal_ptf.objective_values[0].name == ObjectiveName.CVAR
