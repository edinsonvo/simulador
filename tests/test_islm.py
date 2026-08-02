"""Tests del modelo IS-LM."""

import pytest

from sicm_core.analysis.shocks import apply_shock
from sicm_core.engine import dispatch
from sicm_core.experiments import default_scenario
from sicm_core.experiments.scenario import Shock


def _solve(**params):
    scenario = default_scenario("islm")
    if params:
        scenario = new_scenario_with_params(params)
    return dispatch(scenario).solve()


def new_scenario_with_params(params):
    from sicm_core.experiments.scenario import Scenario

    base = default_scenario("islm")
    scenario = Scenario(
        model="islm",
        parameters=base.parameters.with_values(**params),
        metadata=base.metadata,
    )
    return scenario


def test_baseline():
    eq = _solve()
    assert eq.Y == pytest.approx(832.911, rel=1e-3)
    assert eq.r == pytest.approx(0.0443, rel=1e-3)


def test_identities_hold():
    scenario = default_scenario("islm")
    eq = dispatch(scenario).solve()
    assert eq.C + eq.I + scenario.parameters.G == pytest.approx(eq.Y)


def test_multiplier_fiscal():
    model = dispatch(default_scenario("islm"))
    mult = model.multipliers
    assert mult["dY_dG"] == pytest.approx(3.7975, rel=1e-3)


def test_monetary_expansion():
    base = _solve()
    after = _solve(M=350.0 * 1.1)
    assert after.Y > base.Y
    assert after.r < base.r


def test_fiscal_expansion():
    base = _solve()
    after = _solve(G=120.0 * 1.2)
    assert after.Y > base.Y
    assert after.r > base.r
    assert after.I < base.I  # crowding out


def test_tax_increase_contracts():
    base = _solve()
    after = _solve(T=80.0 * 1.1)
    assert after.Y < base.Y


def test_apply_shock_does_not_mutate():
    scenario = default_scenario("islm")
    params_before = scenario.parameters
    shocked = apply_shock(params_before, Shock("G", 0.10))
    assert shocked.G == pytest.approx(132.0)
    assert scenario.parameters.G == 120.0
