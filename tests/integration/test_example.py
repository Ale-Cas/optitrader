"""Test the example code in the documentation."""

import pytest

from optifolio import Optifolio
from optifolio.config import SETTINGS
from optifolio.enums import UniverseName
from optifolio.optimization.objectives import CVaRObjectiveFunction, ObjectiveName

_tollerance = SETTINGS.SUM_WEIGHTS_TOLERANCE


@pytest.mark.timeout(10)
def test_optifolio_example() -> None:
    """Test 1 example."""
    optimal_ptf = Optifolio(
        objectives=[CVaRObjectiveFunction()],
        universe_name=UniverseName.POPULAR_STOCKS,
    ).solve()
    assert 1 - optimal_ptf.weights.values.sum() <= _tollerance
    assert optimal_ptf.objective_values[0].name == ObjectiveName.CVAR
