import pyomo.environ as pyo
import pytest

from stoch_planning.model import PlanningConfig, SCENARIO_NAMES, scenario_creator, scenario_names_creator


def test_scenario_names_are_fixed_and_complete():
    assert scenario_names_creator() == list(SCENARIO_NAMES)
    with pytest.raises(ValueError):
        scenario_names_creator(2)


def test_scenario_tree_metadata_is_three_stage():
    model = scenario_creator("Scen_LH")
    assert model._mpisppy_probability == pytest.approx(0.25)
    assert [node.name for node in model._mpisppy_node_list] == ["ROOT", "ROOT_0"]
    assert [node.stage for node in model._mpisppy_node_list] == [1, 2]
    assert model._mpisppy_node_list[1].parent_name == "ROOT"
    assert model._mpisppy_node_list[0].nonant_vardata_list[0] is model.capacity_expansion
    assert model._mpisppy_node_list[1].nonant_vardata_list[0] is model.stage2_production


def test_scenario_constraints_and_objective_are_constructed():
    model = scenario_creator("Scen_HH")
    assert model.stage2_capacity.active
    assert model.stage3_capacity.active
    assert model.balance1.active and model.balance2.active
    assert model.TotalCost.sense == pyo.minimize


def test_invalid_input_is_rejected():
    with pytest.raises(ValueError, match="unknown scenario"):
        scenario_creator("missing")
    with pytest.raises(ValueError):
        scenario_creator("Scen_LL", PlanningConfig(base_capacity=-1))
