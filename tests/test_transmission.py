"""Canales de transmisión y mecanismo de los cuatro cuadrantes."""

from __future__ import annotations

import pytest

from sicm_core.analysis.shocks import SHOCK_CATALOG
from sicm_core.engine import Engine
from sicm_core.experiments import default_scenario
from sicm_core.experiments.scenario import Shock
from sicm_core.models.four_quadrant import transmission_steps
from sicm_core.results.transmission import CHANNELS_BY_MODEL

ENGINE = Engine()


def _result(model: str):
    spec = SHOCK_CATALOG[model][0]
    scenario = default_scenario(model).with_shocks(
        Shock(spec.target, spec.magnitude, spec.description)
    )
    return ENGINE.run_scenario(scenario)


@pytest.mark.parametrize("model", sorted(CHANNELS_BY_MODEL))
def test_channels_nonempty(model):
    result = _result(model)
    assert result.transmission.channels
    assert result.transmission.description


def test_channels_four_quadrant_ordered():
    result = _result("four_quadrant")
    joined = " → ".join(result.transmission.channels)
    for step in ("IS-LM", "AD-AS", "trabajo"):
        assert step in joined


@pytest.mark.parametrize(
    "target",
    [spec.target for spec in SHOCK_CATALOG["four_quadrant"]],
)
def test_transmission_steps_for_every_target(target):
    base = _result("four_quadrant").baseline
    final = _result("four_quadrant").equilibrium
    steps = transmission_steps(target, base, final)
    assert len(steps) == 4
    assert {s["cuadrante"] for s in steps} == {"II", "III", "IV", "I"}
    assert sum(1 for s in steps if s["valor"] == "origen") == 1


def test_transmission_steps_origin_marker():
    base = _result("four_quadrant").baseline
    final = _result("four_quadrant").equilibrium
    steps = transmission_steps("G", base, final)
    assert steps[0]["cuadrante"] == "II"
    assert steps[0]["valor"] == "origen"
