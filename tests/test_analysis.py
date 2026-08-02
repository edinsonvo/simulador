"""Tests de análisis: choques, políticas y sensibilidad."""

import pytest

from sicm_core.analysis.policy import (
    POLICY_NAMES,
    available_policies,
    policy_shock,
    simulate_policy,
)
from sicm_core.analysis.shocks import SHOCK_CATALOG, apply_shocks, shocks_for
from sicm_core.analysis.sensitivity import one_factor_at_a_time
from sicm_core.engine import Engine
from sicm_core.experiments import default_scenario


def test_shock_catalog_complete():
    assert set(SHOCK_CATALOG) == {
        "islm",
        "mundell_fleming",
        "classical_closed",
        "classical_open",
        "as_ad",
        "islm_bp",
        "new_keynesian",
        "new_classical",
        "okun",
        "phillips",
        "integrated",
        "four_quadrant",
    }
    assert len(shocks_for("islm")) == 6
    assert len(shocks_for("integrated")) == 8


def test_apply_shocks_composes_in_order():
    params = default_scenario("islm").parameters
    g_up, m_up = shocks_for("islm")[0], shocks_for("islm")[4]
    new_params, applied = apply_shocks(params, [g_up, m_up])
    assert applied == [g_up, m_up]
    assert new_params.G == pytest.approx(132.0)
    assert new_params.M == pytest.approx(385.0)
    assert params.G == 120.0


def test_policy_shock():
    shock = policy_shock("fiscal_expansion", 0.15)
    assert shock.target == "G"
    assert shock.magnitude == pytest.approx(0.15)
    assert shock.description


def test_available_policies():
    policies = available_policies()
    assert [p.name for p in policies] == POLICY_NAMES


def test_simulate_policy():
    scenario = default_scenario("islm")
    new_scenario = simulate_policy(scenario, "monetary_expansion", 0.05)
    assert len(new_scenario.shocks) == 1
    assert new_scenario.shocks[0].target == "M"
    assert new_scenario.shocks[0].magnitude == pytest.approx(0.05)


def test_unknown_policy_raises():
    with pytest.raises(KeyError):
        policy_shock("no_existe")


def test_sensitivity_table():
    engine = Engine()
    df = one_factor_at_a_time(
        default_scenario("islm"), "G", [100.0, 120.0, 140.0], engine=engine
    )
    assert len(df) == 3
    assert list(df["G"]) == [100.0, 120.0, 140.0]
    assert "Y" in df.columns
    assert "ΔY (%)" in df.columns
    assert df.loc[df["G"] == 120.0, "ΔY (%)"].iloc[0] == pytest.approx(0.0, abs=1e-9)
