"""Tests del modelo Mundell-Fleming (resultados de referencia verificados)."""

import pytest

from sicm_core.engine import dispatch
from sicm_core.experiments import default_scenario
from sicm_core.experiments.scenario import Scenario, Shock


def _run(shock=None, regime="Flexible"):
    scenario = default_scenario("mundell_fleming")
    metadata = dict(scenario.metadata)
    metadata["regime"] = regime
    scenario = Scenario(model="mundell_fleming",
                        parameters=scenario.parameters,
                        metadata=metadata)
    model = dispatch(scenario)
    if shock is None:
        return model.solve()
    return model.solve_with_shocks([shock])


def test_flexible_baseline():
    base = _run()
    assert base.Y == pytest.approx(550.0, rel=1e-3)
    assert base.e == pytest.approx(201.0, rel=1e-3)


def test_flexible_fiscal_innefective_on_y():
    baseline, final = _run(Shock("G", 0.20))
    assert final.Y == pytest.approx(baseline.Y, rel=1e-3)
    assert final.e == pytest.approx(249.0, rel=1e-3)


def test_flexible_monetary_expansive():
    baseline, final = _run(Shock("M", 0.20))
    assert final.Y == pytest.approx(630.0, rel=1e-3)
    assert final.e == pytest.approx(161.0, rel=1e-3)


def test_fixed_fiscal_expands():
    baseline, final = _run(Shock("G", 0.20), regime="Fijo")
    assert final.Y > baseline.Y
    assert final.M > baseline.M


def test_fixed_regime_endogenous_money():
    baseline, final = _run(Shock("G", 0.20), regime="Fijo")
    assert baseline.M == pytest.approx(201.0, rel=1e-2)
    assert final.M == pytest.approx(249.0, rel=1e-2)
