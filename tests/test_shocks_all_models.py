"""Choques de todos los modelos: cada shock del catálogo debe resolver.

Garantiza que los 12 modelos resuelven su equilibrio base y responden a
todos los choques declarados en :data:`SHOCK_CATALOG`, con valores finitos.
"""

from __future__ import annotations

import math

import pytest

from sicm_core.analysis.shocks import SHOCK_CATALOG, apply_shocks, validate_target
from sicm_core.engine import Engine
from sicm_core.engine.registry import registry
from sicm_core.experiments import default_scenario
from sicm_core.experiments.scenario import Shock

ENGINE = Engine()


def _run(model_name: str, shock: Shock | None = None):
    scenario = default_scenario(model_name)
    if shock is not None:
        scenario = scenario.with_shocks(shock)
    return ENGINE.run_scenario(scenario)


def _finite_count(result) -> int:
    values = [v for v in result.equilibrium.as_dict().values() if v is not None]
    return sum(1 for v in values if math.isfinite(float(v)))


def test_catalog_matches_registry():
    assert set(SHOCK_CATALOG) == set(registry.names())
    for specs in SHOCK_CATALOG.values():
        assert specs, "cada modelo debe tener al menos un choque"


@pytest.mark.parametrize("model", registry.names())
def test_base_equilibrium_solves(model):
    result = _run(model)
    assert result.equilibrium.get("Y") is not None
    assert _finite_count(result) >= 3
    assert result.interpretation.direction == "neutro"


@pytest.mark.parametrize("model", registry.names())
def test_every_catalog_shock_solves(model):
    for spec in SHOCK_CATALOG[model]:
        shock = Shock(
            target=spec.target, magnitude=spec.magnitude, description=spec.description
        )
        result = _run(model, shock)
        assert _finite_count(result) >= 3
        assert result.interpretation.direction in ("expansivo", "contractivo", "neutro")
        assert result.interpretation.bullets


@pytest.mark.parametrize("model", registry.names())
def test_shock_moves_something(model):
    base = _run(model).equilibrium
    shock = Shock(
        target=SHOCK_CATALOG[model][0].target,
        magnitude=SHOCK_CATALOG[model][0].magnitude,
        description=SHOCK_CATALOG[model][0].description,
    )
    final = _run(model, shock).equilibrium
    moved = [
        k
        for k in base.as_dict()
        if base.get(k) is not None
        and final.get(k) is not None
        and abs(final.get(k) - base.get(k)) > 1e-9
    ]
    assert moved, f"{model}: el choque {shock.target} no movió ninguna variable"


def test_apply_shocks_chain():
    scenario = default_scenario("islm").with_shocks(Shock("G", +0.10), Shock("M", -0.10))
    shocked, applied = apply_shocks(scenario.parameters, scenario.shocks)
    assert len(applied) == 2
    assert shocked.G == pytest.approx(scenario.parameters.G * 1.10)
    assert shocked.M == pytest.approx(scenario.parameters.M * 0.90)
    assert shocked is not scenario.parameters


def test_validate_target():
    assert validate_target(default_scenario("islm").parameters, "G")
    assert not validate_target(default_scenario("islm").parameters, "no_existe")
