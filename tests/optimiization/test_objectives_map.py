"""Test objectives map."""


from optitrader.enums.optimization import ObjectiveName
from optitrader.optimization.objectives import FinancialsObjectiveFunction, ObjectivesMap


def test_objectives_map() -> None:
    """Test the ObjectivesMap initialization without objectives and add financials."""
    obj_map = ObjectivesMap()
    obj_map.add_objective(name=ObjectiveName.FINANCIALS)
    assert len(obj_map.objectives) == 1
    assert isinstance(obj_map.objectives[0], FinancialsObjectiveFunction)


def test_objective_latex() -> None:
    """Test the ObjectivesMap initialization without objectives and add financials."""
    obj_map = ObjectivesMap()
    for name in list(ObjectiveName):
        assert obj_map.get_obj_latex(name)
