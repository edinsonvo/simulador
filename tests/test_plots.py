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


def test_plot_four_quadrant_has_positive_slope_labor_curves():
    base, final = _models("four_quadrant")
    fig = plot_four_quadrant(base, final)
    names = {t.name for t in fig.data}
    assert "N^s · Base" in names  # pendiente positiva en (N, W), cuadrante I
    assert "N^d (W) · Base" in names  # demanda nominal en (N, W), cuadrante I
    assert "N^d · Base" in names  # pendiente negativa en (N, W/P), cuadrante IV
    assert "N^s (W/P) · Base" in names  # pendiente positiva en (N, W/P), cuadrante IV


def test_plot_four_quadrant_zooms_labor_subplots():
    base, final = _models("four_quadrant")
    fig = plot_four_quadrant(base, final)
    n_lo, n_hi = fig.layout.xaxis2.range
    assert n_lo < n_hi < 160  # ventana centrada en el equilibrio, no el rango completo
    assert fig.layout.xaxis4.range == (n_lo, n_hi)
    assert fig.layout.yaxis2.range is not None
    assert fig.layout.yaxis4.range is not None


def test_plot_four_quadrant_shock_effect_visible():
    base, final = _models("four_quadrant")
    fig = plot_four_quadrant(base, final)
    n_lo, n_hi = fig.layout.xaxis2.range
    w_lo, w_hi = fig.layout.yaxis2.range
    eq_b, eq_f = base.solve(), final.solve()
    assert eq_b.N != eq_f.N  # el choque mueve el empleo de equilibrio
    assert n_lo <= min(eq_b.N, eq_f.N) and max(eq_b.N, eq_f.N) <= n_hi
    assert w_lo <= min(eq_b.W, eq_f.W) and max(eq_b.W, eq_f.W) <= w_hi


def test_plot_convergence():
    base, _ = _models("four_quadrant")
    fig = plot_convergence(base, periods=10, speed=0.5)
    assert fig.data
