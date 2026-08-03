"""Tests de los modelos nuevos del catálogo (OA-DA, IS-LM-BP,
neokeynesiano, clásico nuevo, Okun, Phillips e integrado)."""

import pytest

from sicm_core.engine import dispatch
from sicm_core.engine.registry import registry
from sicm_core.experiments import default_scenario
from sicm_core.experiments.scenario import Scenario
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
# OA-DA
# ---------------------------------------------------------------------------
def test_as_ad_baseline():
    eq = _solve("as_ad")
    assert eq.Y == pytest.approx(836.1, rel=1e-3)
    assert eq.P == pytest.approx(0.918, rel=1e-3)
    assert eq.gap == pytest.approx(-0.164, rel=1e-2)


def test_as_ad_long_run_returns_natural():
    base = default_scenario("as_ad")
    scenario = Scenario(
        model="as_ad", parameters=base.parameters, metadata={"horizon": "largo"}
    )
    eq = dispatch(scenario).solve()
    assert eq.Y == pytest.approx(base.parameters.Yn)
    assert eq.gap == pytest.approx(0.0, abs=1e-9)


def test_as_ad_fiscal_expansion():
    base = _solve("as_ad")
    after = _solve("as_ad", G=132.0)
    assert after.Y > base.Y
    assert after.P > base.P


def test_as_ad_monetary_expansion():
    base = _solve("as_ad")
    after = _solve("as_ad", M=385.0)
    assert after.Y > base.Y
    assert after.P > base.P
    assert after.r < base.r


# ---------------------------------------------------------------------------
# IS-LM-BP
# ---------------------------------------------------------------------------
def test_islm_bp_baseline_clears_bp():
    eq = _solve("islm_bp")
    assert eq.BP == pytest.approx(0.0, abs=1e-6)


def test_islm_bp_fiscal_expansion():
    base = _solve("islm_bp")
    after = _solve("islm_bp", G=132.0)
    assert after.Y > base.Y
    assert after.r > base.r


def test_islm_bp_monetary_expansion():
    base = _solve("islm_bp")
    after = _solve("islm_bp", M=385.0)
    assert after.Y > base.Y
    assert after.r < base.r


def test_islm_bp_fixed_regime_anchors_exchange_rate():
    base = default_scenario("islm_bp")
    scenario = Scenario(
        model="islm_bp", parameters=base.parameters, metadata={"regime": "fijo"}
    )
    eq = dispatch(scenario).solve()
    assert eq.e == pytest.approx(base.parameters.e_bar)


# ---------------------------------------------------------------------------
# Neokeynesiano
# ---------------------------------------------------------------------------
def test_new_keynesian_baseline():
    eq = _solve("new_keynesian")
    assert eq.Y == pytest.approx(994.5, rel=1e-3)
    assert eq.pi == pytest.approx(0.0273, abs=1e-4)


def test_new_keynesian_fiscal_expansion():
    base = _solve("new_keynesian")
    after = _solve("new_keynesian", G=132.0)
    assert after.Y > base.Y
    assert after.pi > base.pi
    assert after.r > base.r


def test_new_keynesian_higher_target_raises_inflation_and_gap():
    base = _solve("new_keynesian")
    after = _solve("new_keynesian", pi_target=0.03)
    assert after.pi > base.pi
    assert after.gap > base.gap
    assert after.r < base.r


# ---------------------------------------------------------------------------
# Clásico nuevo
# ---------------------------------------------------------------------------
def test_new_classical_baseline_at_natural():
    eq = _solve("new_classical")
    assert eq.Y == pytest.approx(1000.0, rel=1e-3)
    assert eq.gap == pytest.approx(0.0, abs=1e-9)


def test_new_classical_surprise_moves_output():
    base = _solve("new_classical")
    after = _solve("new_classical", M=1100.0)
    assert after.Y > base.Y


def test_new_classical_anticipated_money_neutral():
    base = default_scenario("new_classical")
    scenario = Scenario(
        model="new_classical",
        parameters=base.parameters.with_values(M=1100.0),
        metadata={"expectativas": "anticipadas"},
    )
    eq = dispatch(scenario).solve()
    assert eq.Y == pytest.approx(base.parameters.Yn)
    assert eq.P == pytest.approx(1.1, rel=1e-3)


# ---------------------------------------------------------------------------
# Ley de Okun y curva de Phillips
# ---------------------------------------------------------------------------
def test_okun_output_above_natural_lowers_unemployment():
    eq = _solve("okun", Y_obs=1050.0)
    assert eq.gap == pytest.approx(0.05, rel=1e-3)
    assert eq.u == pytest.approx(0.06 - 2.0 * 0.05, rel=1e-3)


def test_phillips_output_above_natural_raises_inflation():
    eq = _solve("phillips", Y_obs=1050.0)
    assert eq.pi == pytest.approx(0.03 + 0.5 * 0.05, rel=1e-3)


# ---------------------------------------------------------------------------
# Modelo integrado
# ---------------------------------------------------------------------------
def test_integrated_baseline_full_employment():
    eq = _solve("integrated")
    assert eq.Y == pytest.approx(1000.0, rel=1e-3)
    assert eq.gap == pytest.approx(0.0, abs=1e-9)
    assert eq.BP == pytest.approx(0.0, abs=1e-9)


def test_integrated_fiscal_expansion_raises_gap():
    base = _solve("integrated")
    after = _solve("integrated", G=132.0)
    assert after.Y > base.Y
    assert after.gap > base.gap
    assert after.pi > base.pi
    assert after.u < base.u


def test_integrated_money_neutral_in_real_terms():
    base = _solve("integrated")
    after = _solve("integrated", M=385.0)
    assert after.Y == pytest.approx(base.Y)
    assert after.P > base.P


# ---------------------------------------------------------------------------
# Interpretación de los nuevos modelos
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "name",
    [
        "as_ad",
        "islm_bp",
        "new_keynesian",
        "new_classical",
        "okun",
        "phillips",
        "integrated",
    ],
)
def test_interpretation_builds_for_new_models(name):
    scenario = default_scenario(name)
    model = dispatch(scenario)
    base = model.solve()
    final = model.solve()
    interp = build_interpretation(model, base, final, [])
    assert interp.title
    assert interp.summary
    assert interp.direction in {"expansivo", "contractivo", "neutro"}


def test_all_new_models_registered():
    names = set(registry.names())
    assert {
        "as_ad",
        "islm_bp",
        "new_keynesian",
        "new_classical",
        "okun",
        "phillips",
        "integrated",
    } <= names
