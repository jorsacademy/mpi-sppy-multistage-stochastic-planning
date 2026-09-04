from __future__ import annotations

from dataclasses import dataclass

import pyomo.environ as pyo
from mpisppy.scenario_tree import ScenarioNode

SCENARIO_DATA = {
    "Scen_LL": (4.0, 5.0, 0, 0),
    "Scen_LH": (4.0, 9.0, 0, 1),
    "Scen_HL": (8.0, 5.0, 1, 0),
    "Scen_HH": (8.0, 9.0, 1, 1),
}
SCENARIO_NAMES = tuple(SCENARIO_DATA)


@dataclass(frozen=True)
class PlanningConfig:
    initial_inventory: float = 3.0
    base_capacity: float = 5.0
    capacity_cost: float = 2.0
    production_cost: float = 1.0
    holding_cost: float = 0.4
    shortage_cost: float = 5.0
    max_capacity_expansion: float = 8.0

    def validate(self) -> None:
        if self.initial_inventory < 0 or self.base_capacity < 0:
            raise ValueError("inventory and capacity must be non-negative")
        if self.max_capacity_expansion < 0:
            raise ValueError("max_capacity_expansion must be non-negative")
        if min(self.capacity_cost, self.production_cost, self.holding_cost, self.shortage_cost) < 0:
            raise ValueError("cost coefficients must be non-negative")


def scenario_names_creator(num_scens: int = 4, start: int = 0) -> list[str]:
    if start != 0 or num_scens != 4:
        raise ValueError("this demonstration uses exactly four scenarios")
    return list(SCENARIO_NAMES)


def scenario_creator(scenario_name: str, config: PlanningConfig | None = None) -> pyo.ConcreteModel:
    if scenario_name not in SCENARIO_DATA:
        raise ValueError(f"unknown scenario: {scenario_name}")
    config = config or PlanningConfig()
    config.validate()
    demand1, demand2, branch1, _ = SCENARIO_DATA[scenario_name]

    m = pyo.ConcreteModel(name=scenario_name)
    m.capacity_expansion = pyo.Var(bounds=(0, config.max_capacity_expansion))
    m.stage2_production = pyo.Var(domain=pyo.NonNegativeReals)
    m.stage3_production = pyo.Var(domain=pyo.NonNegativeReals)
    m.inv1 = pyo.Var(domain=pyo.NonNegativeReals)
    m.short1 = pyo.Var(domain=pyo.NonNegativeReals)
    m.inv2 = pyo.Var(domain=pyo.NonNegativeReals)
    m.short2 = pyo.Var(domain=pyo.NonNegativeReals)

    capacity = config.base_capacity + m.capacity_expansion
    m.stage2_capacity = pyo.Constraint(expr=m.stage2_production <= capacity)
    m.stage3_capacity = pyo.Constraint(expr=m.stage3_production <= capacity)
    m.balance1 = pyo.Constraint(
        expr=m.inv1 - m.short1 == config.initial_inventory + m.stage2_production - demand1
    )
    m.balance2 = pyo.Constraint(
        expr=m.inv2 - m.short2 == m.inv1 - m.short1 + m.stage3_production - demand2
    )

    m.Stage1Cost = pyo.Expression(expr=config.capacity_cost * m.capacity_expansion)
    m.Stage2Cost = pyo.Expression(
        expr=config.production_cost * m.stage2_production
        + config.holding_cost * m.inv1
        + config.shortage_cost * m.short1
    )
    m.Stage3Cost = pyo.Expression(
        expr=config.production_cost * m.stage3_production
        + config.holding_cost * m.inv2
        + config.shortage_cost * m.short2
    )
    m.TotalCost = pyo.Objective(expr=m.Stage1Cost + m.Stage2Cost + m.Stage3Cost, sense=pyo.minimize)

    branch_node = f"ROOT_{branch1}"
    m._mpisppy_probability = 0.25
    m._mpisppy_node_list = [
        ScenarioNode("ROOT", 1.0, 1, m.Stage1Cost, [m.capacity_expansion], m),
        ScenarioNode(
            branch_node,
            0.5,
            2,
            m.Stage2Cost,
            [m.stage2_production],
            m,
            parent_name="ROOT",
        ),
    ]
    return m


def kw_creator(config: PlanningConfig | None = None) -> dict[str, PlanningConfig]:
    return {"config": config or PlanningConfig()}


def inparser_adder(cfg) -> None:
    return None


def scenario_denouement(rank, scenario_name, scenario) -> None:
    return None
