"""Tests del registro y despacho de modelos."""

import pytest

import sicm_core
from sicm_core.engine.dispatcher import dispatch
from sicm_core.engine.registry import ModelNotFoundError, registry


def test_models_registered():
    assert {"islm", "mundell_fleming", "classical_closed", "classical_open"} <= set(
        registry.names()
    )


def test_families():
    families = registry.families()
    assert families["keynesian"] == ["islm", "mundell_fleming"]
    assert set(families["classical"]) == {"classical_closed", "classical_open"}


def test_labels_present():
    labels = registry.labels()
    assert "IS-LM (economía cerrada)" in labels.values()


def test_unknown_model_raises():
    with pytest.raises(ModelNotFoundError):
        registry.get("no_existe")


def test_dispatch_builds_model():
    from sicm_core.experiments import default_scenario

    scenario = default_scenario("islm")
    model = dispatch(scenario)
    assert model.name == "islm"
    assert model.parameters is scenario.parameters


def test_catalog_from_engine():
    engine = sicm_core.Engine()
    names = {item["name"] for item in engine.catalog()}
    assert names == set(registry.names())
