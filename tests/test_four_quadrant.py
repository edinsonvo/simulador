"""Tests del modelo de equilibrio general de cuatro cuadrantes."""

import pytest

from sicm_core.engine import dispatch
from sicm_core.engine.registry import registry
from sicm_core.experiments import default_scenario
from sicm_core.experiments.scenario import Scenario
from sicm_core.models.four_quadrant import transmission_steps
from sicm_core.results.interpretation import build_interpretation


def _solve(name, **updates):
    base = default_scenario(name)
    scenario = Scenario(
        model=name,
        parameters=base.parameters.with_values(**updates) if updates else base.parameters,
        metadata=base.metadata,
    )
    return dispatch(scenario).solve()


# ---------------------------------------------------------------------------
# Equilibrio de referencia
# ---------------------------------------------------------------------------
def test_four_quadrant_baseline_at_full_employment():
    eq = _solve("four_quadrant")
    assert eq.Y == pytest.approx(1000.0, rel=1e-3)
    assert eq.P == pytest.approx(1.0, rel=1e-3)
    assert eq.r == pytest.approx(0.06, rel=1e-3)
    assert eq.N == pytest.approx(100.0, rel=1e-3)
    assert eq.w == pytest.approx(5.0, rel=1e-3)
    assert eq.W == pytest.approx(5.0, rel=1e-3)
    assert eq.u == pytest.approx(0.0, abs=1e-9)


def test_four_quadrant_long_run_returns_natural():
    base = default_scenario("four_quadrant")
    scenario = Scenario(
        model="four_quadrant", parameters=base.parameters, metadata={"horizon": "largo"}
    )
    eq = dispatch(scenario).solve()
    assert eq.Y == pytest.approx(base.parameters.Yn)
    assert eq.gap == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# Cadenas de transmisión
# ---------------------------------------------------------------------------
def test_four_quadrant_fiscal_expansion_chain():
    base = _solve("four_quadrant")
    after = _solve("four_quadrant", G=132.0)
    assert after.Y > base.Y  # IS -> ↑Y
    assert after.P > base.P  # -> ↑P
    assert after.w < base.w  # -> ↓W/P
    assert after.N > base.N  # -> ↑N
    assert after.W > base.W  # -> ↑W


def test_four_quadrant_monetary_expansion_chain():
    base = _solve("four_quadrant")
    after = _solve("four_quadrant", M=860.0)
    assert after.r < base.r  # LM -> ↓i
    assert after.Y > base.Y
    assert after.P > base.P
    assert after.N > base.N


def test_four_quadrant_productivity_chain():
    base = _solve("four_quadrant")
    after = _solve("four_quadrant", A_prod=110.0)
    assert after.P < base.P  # AS -> ↓P
    assert after.Y > base.Y
    assert after.w > base.w  # -> ↑W/P
    assert after.W > base.W  # -> ↑W


def test_four_quadrant_expectations_chain():
    base = _solve("four_quadrant")
    after = _solve("four_quadrant", Pe=1.1)
    assert after.P > base.P  # AS -> ↑P
    assert after.Y < base.Y
    assert after.N < base.N


def test_four_quadrant_multipliers_positive():
    m = dispatch(default_scenario("four_quadrant"))
    mult = m.multipliers
    assert mult["dY_dG"] > 0
    assert mult["dY_dM"] > 0


# ---------------------------------------------------------------------------
# Dinámica y transmisión
# ---------------------------------------------------------------------------
def test_four_quadrant_dynamic_converges():
    base = default_scenario("four_quadrant")
    model = dispatch(
        Scenario(
            model="four_quadrant",
            parameters=base.parameters.with_values(G=132.0),
            metadata=base.metadata,
        )
    )
    path = model.dynamic_simulation(periods=30, speed=0.3)
    last = path[-1]
    assert abs(last["Y"] - last["Yn"]) < 1.0  # converge al natural
    assert abs(last["P"] - last["Pe"]) < 1e-3  # expectativas cumplidas


def test_four_quadrant_transmission_steps():
    base = _solve("four_quadrant")
    after = _solve("four_quadrant", G=132.0)
    steps = transmission_steps("G", base, after)
    assert len(steps) == 4
    assert [s["cuadrante"] for s in steps] == ["II", "III", "IV", "I"]
    assert steps[0]["valor"] == "origen"
    assert all(s["detalle"] for s in steps)


def test_four_quadrant_interpretation_builds():
    model = dispatch(default_scenario("four_quadrant"))
    base = model.solve()
    final = _solve("four_quadrant", G=132.0)
    interp = build_interpretation(model, base, final, [])
    assert interp.title
    assert interp.summary
    assert interp.direction == "expansivo"


def test_four_quadrant_registered():
    assert "four_quadrant" in set(registry.names())
