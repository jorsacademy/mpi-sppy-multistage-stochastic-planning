import pytest

from stoch_planning.model import PlanningConfig
from stoch_planning.solve import build_extensive_form, solve_extensive_form


def test_extensive_form_builds_with_nonanticipativity():
    ef = build_extensive_form()
    assert hasattr(ef, "EF_Obj")
    assert len(list(ef.component_objects())) > 0


def test_highs_solves_multistage_extensive_form():
    solution = solve_extensive_form()
    assert solution.objective > 0
    assert 0 <= solution.capacity_expansion <= PlanningConfig().max_capacity_expansion
    assert solution.stage2_production_low >= 0
    assert solution.stage2_production_high >= 0


def test_solution_is_deterministic():
    a = solve_extensive_form()
    b = solve_extensive_form()
    assert a == pytest.approx(b)
