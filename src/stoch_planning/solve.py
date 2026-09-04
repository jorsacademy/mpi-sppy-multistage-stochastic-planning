from __future__ import annotations

from dataclasses import dataclass

import pyomo.environ as pyo
from mpisppy.utils import sputils

from .model import PlanningConfig, SCENARIO_NAMES, scenario_creator


@dataclass(frozen=True)
class PlanningSolution:
    objective: float
    capacity_expansion: float
    stage2_production_low: float
    stage2_production_high: float


def build_extensive_form(config: PlanningConfig | None = None):
    cfg = config or PlanningConfig()
    return sputils.create_EF(
        list(SCENARIO_NAMES),
        scenario_creator,
        scenario_creator_kwargs={"config": cfg},
        EF_name="multistage_production_ef",
        suppress_warnings=True,
    )


def solve_extensive_form(config: PlanningConfig | None = None) -> PlanningSolution:
    ef = build_extensive_form(config)
    solver = pyo.SolverFactory("appsi_highs")
    if solver is None or not solver.available(exception_flag=False):
        raise RuntimeError("HiGHS solver is not available")
    results = solver.solve(ef)
    term = str(results.solver.termination_condition).lower()
    if "optimal" not in term:
        raise RuntimeError(f"solver did not reach optimality: {term}")

    scenarios = {name: model for name, model in sputils.ef_scenarios(ef)}
    ll = scenarios["Scen_LL"]
    lh = scenarios["Scen_LH"]
    hl = scenarios["Scen_HL"]
    hh = scenarios["Scen_HH"]

    low = float(pyo.value(ll.stage2_production))
    high = float(pyo.value(hl.stage2_production))
    if abs(low - float(pyo.value(lh.stage2_production))) > 1e-7:
        raise RuntimeError("low-branch nonanticipativity violated")
    if abs(high - float(pyo.value(hh.stage2_production))) > 1e-7:
        raise RuntimeError("high-branch nonanticipativity violated")

    return PlanningSolution(
        objective=float(pyo.value(ef.EF_Obj)),
        capacity_expansion=float(pyo.value(ll.capacity_expansion)),
        stage2_production_low=low,
        stage2_production_high=high,
    )
