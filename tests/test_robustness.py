"""Tests de robustez: solver 1D, validación de parámetros y motor."""

import numpy as np
import pytest

from sicm_core.engine import Engine
from sicm_core.engine.errors import SimulationError, validate_parameters
from sicm_core.engine.registry import ModelNotFoundError
from sicm_core.experiments import default_scenario, new_experiment
from sicm_core.experiments.scenario import Scenario
from sicm_core.models.solvers import solve_1d


# ---------------------------------------------------------------------------
# solve_1d
# ---------------------------------------------------------------------------
def test_solve_1d_finds_crossing():
    root = solve_1d(lambda x: x - 5.0, 0.0, 10.0)
    assert root == pytest.approx(5.0, abs=1e-9)


def test_solve_1d_exact_zero_at_sample():
    root = solve_1d(lambda x: x, -1.0, 1.0, n=11)
    assert root == pytest.approx(0.0, abs=1e-9)


def test_solve_1d_skips_non_finite_and_finds_root():
    def f(x):
        if abs(x - 2.0) < 0.5:
            return np.nan
        return x - 8.0

    assert solve_1d(f, 0.0, 10.0) == pytest.approx(8.0, abs=1e-9)


def test_solve_1d_argmin_fallback_when_tangent():
    # Sin cruce (función tangente al eje), debe devolver el mínimo cercano a cero.
    root = solve_1d(lambda x: (x - 3.0) ** 2, 0.0, 6.0)
    assert root == pytest.approx(3.0, abs=1e-2)


def test_solve_1d_raises_when_no_root():
    with pytest.raises(ValueError):
        solve_1d(lambda x: x * x + 1.0, -10.0, 10.0)


def test_solve_1d_rejects_bad_interval():
    with pytest.raises(ValueError):
        solve_1d(lambda x: x, 5.0, 2.0)


# ---------------------------------------------------------------------------
# Validación de parámetros
# ---------------------------------------------------------------------------
def test_validate_parameters_accepts_finite():
    validate_parameters("test", default_scenario("islm").parameters)


def test_validate_parameters_rejects_nan():
    params = default_scenario("islm").parameters.with_values(G=float("nan"))
    with pytest.raises(SimulationError, match="G"):
        validate_parameters("islm", params)


def test_validate_parameters_rejects_inf():
    params = default_scenario("islm").parameters.with_values(M=float("inf"))
    with pytest.raises(SimulationError):
        validate_parameters("islm", params)


# ---------------------------------------------------------------------------
# Motor: errores legibles
# ---------------------------------------------------------------------------
def test_engine_wraps_solve_errors_in_simulation_error():
    engine = Engine()
    scenario = Scenario(
        model="four_quadrant",
        parameters=default_scenario("four_quadrant").parameters.with_values(
            alpha_prod=0.0, Nn=0.0
        ),
    )
    experiment = new_experiment(name="x", scenario=scenario)
    with pytest.raises(SimulationError):
        engine.run(experiment)
    assert experiment.status == "failed"


def test_engine_passes_through_unknown_model():
    engine = Engine()
    scenario = Scenario(model="nope", parameters=default_scenario("islm").parameters)
    experiment = new_experiment(name="x", scenario=scenario)
    with pytest.raises(ModelNotFoundError):
        engine.run(experiment)
    assert experiment.status == "failed"
