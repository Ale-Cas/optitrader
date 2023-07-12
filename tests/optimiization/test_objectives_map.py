"""Test objectives map."""


from optifolio.enums.optimization import ObjectiveName
from optifolio.optimization.objectives import FinancialsObjectiveFunction, ObjectivesMap


def test_objectives_map() -> None:
    """Test the ObjectivesMap initialization without objectives and add financials."""
    obj_map = ObjectivesMap()
    obj_map.add_objective(name=ObjectiveName.FINANCIALS)
    assert len(obj_map.objectives) == 1
    assert isinstance(obj_map.objectives[0], FinancialsObjectiveFunction)
