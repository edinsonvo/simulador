"""Las funciones de gráfica devuelven figuras plotly válidas para cada modelo."""

from __future__ import annotations

import pytest

from research_lab.visualization.plots import (
    plot_as_ad,
    plot_comparison,
    plot_convergence,
    plot_four_quadrant,
    plot_integrated,
    plot_is_lm,
    plot_islm_bp,
    plot_mundell_fleming,
    plot_okun,
    plot_phillips,
    plot_result,
    plot_transmission_mechanism,
)
from sicm_core.analysis.shocks import SHOCK_CATALOG, apply_shocks
from sicm_core.engine import Engine
from sicm_core.engine.dispatcher import dispatch
from sicm_core.experiments import default_scenario
from sicm_core.experiments.scenario import Scenario
from sicm_core.models.four_quadrant import transmission_steps

ENGINE = Engine()
MODELS = sorted(SHOCK_CATALOG)


def _models(model_name: str):
    scenario = default_scenario(model_name)
    base = dispatch(scenario)
    shock = _spec_shock(SHOCK_CATALOG[model_name][0])
    shocked, _ = apply_shocks(scenario.parameters, [shock])
    final = dispatch(
        Scenario(model=model_name, parameters=shocked, metadata=scenario.metadata)
    )
    return base, final


def _spec_shock(spec):
    from sicm_core.experiments.scenario import Shock

    return Shock(spec.target, spec.magnitude, spec.description)


def _result(model_name: str):
    scenario = default_scenario(model_name).with_shocks(
        _spec_shock(SHOCK_CATALOG[model_name][0])
    )
    return ENGINE.run_scenario(scenario)


@pytest.mark.parametrize("model", MODELS)
def test_plot_result_returns_figure(model):
    result = _result(model)
    base, final = _models(model)
    fig = plot_result(result, base, final)
    assert fig.data, f"{model}: figura sin trazas"


@pytest.mark.parametrize("model", MODELS)
def test_plot_comparison_returns_figure(model):
    fig = plot_comparison(_result(model))
    assert fig.data


def test_specific_curve_plots():
    for name, fn in [
        ("islm", plot_is_lm),
        ("mundell_fleming", plot_mundell_fleming),
        ("as_ad", plot_as_ad),
        ("islm_bp", plot_islm_bp),
        ("okun", plot_okun),
        ("phillips", plot_phillips),
        ("integrated", plot_integrated),
        ("four_quadrant", plot_four_quadrant),
    ]:
        base, final = _models(name)
        fig = fn(base, final)
        assert fig.data, f"{name}: figura sin trazas"


def test_plot_transmission_mechanism():
    result = _result("four_quadrant")
    steps = transmission_steps("G", result.baseline, result.equilibrium)
    fig = plot_transmission_mechanism(steps, result.baseline, result.equilibrium)
    assert len(fig.layout.shapes) == 4
    assert len(fig.layout.annotations) >= 8


def test_plot_convergence():
    base, _ = _models("four_quadrant")
    fig = plot_convergence(base, periods=10, speed=0.5)
    assert fig.data
