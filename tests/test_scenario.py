"""Tests de parámetros, choques y escenarios."""

import pytest

from sicm_core.experiments import default_scenario, new_scenario
from sicm_core.experiments.scenario import EconomyParameters, Shock


def test_from_mapping_filters_unknown():
    params = EconomyParameters.from_mapping({"G": 150.0, "no_existe": 1.0})
    assert params.G == 150.0
    assert not hasattr(params, "no_existe")


def test_from_mapping_rejects_non_numeric():
    with pytest.raises(ValueError):
        EconomyParameters.from_mapping({"G": "abc"})


def test_with_values_immutable():
    params = EconomyParameters(G=120.0)
    new = params.with_values(G=150.0)
    assert params.G == 120.0
    assert new.G == 150.0


def test_as_dict_contains_all_fields():
    data = EconomyParameters().as_dict()
    assert data["M"] == 350.0
    assert set(data) == set(EconomyParameters.__dataclass_fields__)


def test_shock_relative():
    params = EconomyParameters(G=100.0)
    shocked = Shock("G", 0.10).apply_to(params)
    assert shocked.G == pytest.approx(110.0)


def test_shock_absolute():
    params = EconomyParameters(G=100.0)
    shocked = Shock("G", 5.0, absolute=True).apply_to(params)
    assert shocked.G == pytest.approx(105.0)


def test_shock_does_not_mutate():
    params = EconomyParameters(G=100.0)
    Shock("G", 0.10).apply_to(params)
    assert params.G == 100.0


def test_default_scenario_islm_calibration():
    scenario = default_scenario("islm")
    assert scenario.parameters.M == 350.0
    assert scenario.parameters.h == 1500.0


def test_default_scenario_mf_metadata():
    scenario = default_scenario("mundell_fleming")
    assert scenario.parameters.kappa == 1e9


def test_with_shocks_appends():
    scenario = default_scenario("islm")
    scenario = scenario.with_shocks(Shock("G", 0.10))
    assert len(scenario.shocks) == 1
    scenario = scenario.with_shocks(Shock("M", -0.05))
    assert len(scenario.shocks) == 2


def test_new_scenario_label():
    scenario = new_scenario("islm", EconomyParameters(), label="mi escenario")
    assert scenario.label == "mi escenario"
