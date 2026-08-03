"""Tests de I/O: JSON, persistencia y Excel."""

from __future__ import annotations

from sicm_core.analysis.shocks import shocks_for
from sicm_core.engine import Engine
from sicm_core.experiments import default_scenario, new_experiment
from sicm_core.io import (
    ExperimentStore,
    experiment_from_dict,
    experiment_to_dict,
    load_json,
    result_to_excel,
    save_json,
    scenario_from_dict,
    scenario_to_dict,
)


def _completed_experiment():
    engine = Engine()
    scenario = default_scenario("islm").with_shocks(shocks_for("islm")[0])
    experiment = new_experiment(
        name="G+10%", description="test", author="qa", scenario=scenario
    )
    engine.run(experiment)
    return experiment


def test_scenario_roundtrip():
    scenario = default_scenario("mundell_fleming").with_shocks(
        shocks_for("mundell_fleming")[0]
    )
    restored = scenario_from_dict(scenario_to_dict(scenario))
    assert restored.model == scenario.model
    assert len(restored.shocks) == 1
    assert restored.parameters.M == scenario.parameters.M
    assert restored.metadata == scenario.metadata


def test_experiment_roundtrip():
    exp = _completed_experiment()
    restored = experiment_from_dict(experiment_to_dict(exp))
    assert restored.id == exp.id
    assert restored.name == exp.name
    assert restored.result is not None
    assert restored.result.equilibrium["Y"] == exp.result.equilibrium["Y"]
    assert restored.result.interpretation.title == exp.result.interpretation.title


def test_save_load_file(tmp_path):
    exp = _completed_experiment()
    path = tmp_path / "exp.json"
    save_json(exp, path)
    restored = load_json(path)
    assert restored.id == exp.id
    assert restored.result is not None


def test_store_lifecycle(tmp_path):
    store = ExperimentStore(tmp_path / "store")
    exp = _completed_experiment()
    store.save(exp)
    assert store.count() == 1
    assert store.exists(exp.id)
    loaded = store.load(exp.id)
    assert loaded.name == exp.name
    store.delete(exp.id)
    assert store.count() == 0


def test_store_clear(tmp_path):
    store = ExperimentStore(tmp_path / "store")
    store.save_many([_completed_experiment(), _completed_experiment()])
    assert store.count() == 2
    store.clear()
    assert store.count() == 0


def test_result_to_excel(tmp_path):
    result = _completed_experiment().result
    path = result_to_excel(result, tmp_path / "out.xlsx")
    assert path.exists()
    assert path.stat().st_size > 1000
