"""Tests del motor de simulación."""

import pytest

from sicm_core.analysis.shocks import shocks_for
from sicm_core.engine import Engine
from sicm_core.experiments import default_scenario, new_experiment


@pytest.fixture
def engine():
    return Engine()


def test_run_sets_result_and_status(engine):
    scenario = default_scenario("islm").with_shocks(shocks_for("islm")[0])
    experiment = new_experiment(name="test", scenario=scenario)
    result = engine.run(experiment)
    assert experiment.status == "completed"
    assert experiment.result is result
    assert result.equilibrium is not None
    assert result.baseline is not None


def test_run_no_shock_uses_same_equilibrium(engine):
    scenario = default_scenario("classical_closed")
    experiment = new_experiment(name="base", scenario=scenario)
    result = engine.run(experiment)
    assert result.equilibrium == result.baseline


def test_run_scenario(engine):
    result = engine.run_scenario(default_scenario("islm"))
    assert result.equilibrium.Y > 0


def test_run_many(engine):
    experiments = [
        new_experiment(name=f"e{i}", scenario=default_scenario("islm")) for i in range(3)
    ]
    results = engine.run_many(experiments)
    assert len(results) == 3
    assert all(e.status == "completed" for e in experiments)


def test_compare(engine):
    experiments = [
        new_experiment(name="base", scenario=default_scenario("islm")),
        new_experiment(
            name="choque",
            scenario=default_scenario("islm").with_shocks(shocks_for("islm")[0]),
        ),
    ]
    df = engine.compare(experiments)
    assert list(df["experiment"]) == ["base", "choque"]
    assert "ΔY (%)" in df.columns


def test_unknown_model_raises(engine):
    from sicm_core.engine.registry import ModelNotFoundError
    from sicm_core.experiments.scenario import Scenario

    scenario = Scenario(model="nope", parameters=default_scenario("islm").parameters)
    experiment = new_experiment(name="x", scenario=scenario)
    with pytest.raises(ModelNotFoundError):
        engine.run(experiment)


def test_solve_with_shocks_does_not_mutate_scenario(engine):
    scenario = default_scenario("islm").with_shocks(shocks_for("islm")[0])
    params_before = scenario.parameters
    engine.run(new_experiment(name="x", scenario=scenario))
    assert scenario.parameters is params_before
    assert scenario.parameters.G == 120.0
