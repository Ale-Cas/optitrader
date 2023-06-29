"""Test the example code in the documentation."""

from optifolio import Optifolio
from optifolio.enums import UniverseName
from optifolio.optimization.objectives import CVaRObjectiveFunction, ObjectiveName


def test_optifolio_example() -> None:
    """Test 1 example."""
    _tollerance = 1e-4
    optimal_ptf = Optifolio(
        objectives=[CVaRObjectiveFunction()],
        universe_name=UniverseName.POPULAR_STOCKS,
    ).solve()
    assert 1 - optimal_ptf.weights.values.sum() <= _tollerance
    assert optimal_ptf.objective_values[0].name == ObjectiveName.CVAR
