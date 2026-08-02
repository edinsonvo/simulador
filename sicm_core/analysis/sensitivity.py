"""Análisis de sensibilidad de los modelos."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from ..engine.engine import Engine
from ..experiments.experiment import new_experiment
from ..experiments.scenario import Scenario


def one_factor_at_a_time(
    scenario: Scenario,
    parameter: str,
    values: Iterable[float],
    engine: Engine | None = None,
) -> pd.DataFrame:
    """Análisis unifactorial: barre ``parameter`` sobre ``values``.

    Para cada valor, ejecuta el escenario (sin choques) y registra el
    equilibrio resultante junto con la desviación respecto a la base.
    """
    engine = engine or Engine()
    baseline = engine.run_scenario(scenario).equilibrium
    rows = []
    for value in values:
        params = scenario.parameters.with_values(**{parameter: value})
        run_scenario = Scenario(
            model=scenario.model,
            parameters=params,
            metadata=scenario.metadata,
            label=f"{parameter}={value:g}",
        )
        experiment = new_experiment(name=f"Sensibilidad {parameter}", scenario=run_scenario)
        result = engine.run(experiment)
        eq = result.equilibrium
        row = {parameter: value}
        for key in eq.keys():
            row[key] = eq[key]
            base = baseline.get(key)
            if base:
                row[f"Δ{key} (%)"] = (eq[key] - base) / base * 100.0
        rows.append(row)
    return pd.DataFrame(rows)


def sensitivity_table(
    scenario: Scenario,
    parameter: str,
    grid: Iterable[float],
    engine: Engine | None = None,
) -> pd.DataFrame:
    """Alias de :func:`one_factor_at_a_time` (tabla de sensibilidad)."""
    return one_factor_at_a_time(scenario, parameter, grid, engine=engine)
