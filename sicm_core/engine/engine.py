"""Motor de simulación: ejecuta experimentos y produce resultados."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from ..experiments.experiment import Experiment, new_experiment
from ..experiments.scenario import Scenario
from ..results.equilibrium import EquilibriumResult, build_result
from .dispatcher import dispatch
from .errors import SimulationError, validate_parameters
from .registry import ModelNotFoundError, ModelRegistry
from .registry import registry as default_registry


class Engine:
    """Motor de simulación de SICM.

    El motor no conoce modelos concretos: recibe un :class:`Experiment`
    con un :class:`Scenario`, despacha al modelo registrado, resuelve el
    equilibrio base y el equilibrio con choques, y ensambla un
    :class:`EquilibriumResult`.
    """

    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry or default_registry

    # -- Ejecución ----------------------------------------------------------
    def run(self, experiment: Experiment, auto_plots: bool = False) -> EquilibriumResult:
        """Ejecuta un experimento y devuelve su resultado.

        Actualiza ``experiment.result`` y ``experiment.status``.
        """
        if experiment.result is not None:
            return experiment.result
        experiment.status = "running"
        try:
            model = dispatch(experiment.scenario)
            validate_parameters(model.name, model.parameters)
            baseline = model.solve()
            shocks = list(experiment.scenario.shocks)
            if shocks:
                final = model.solve_with_shocks(shocks)[1]
            else:
                final = baseline
            result = build_result(model, baseline, final, shocks)
            experiment.result = result
            experiment.status = "completed"
            return result
        except (SimulationError, ModelNotFoundError):
            experiment.status = "failed"
            raise
        except Exception as exc:  # pragma: no cover - control de estado
            experiment.status = "failed"
            raise SimulationError(
                f"No se pudo resolver el modelo «{experiment.scenario.model}»: {exc}"
            ) from exc

    def run_scenario(
        self, scenario: Scenario, name: str = "Simulación"
    ) -> EquilibriumResult:
        """Ejecuta un escenario ad hoc sin construir un experimento explícito."""
        experiment = new_experiment(name=name, scenario=scenario)
        return self.run(experiment)

    def run_many(self, experiments: Iterable[Experiment]) -> list[EquilibriumResult]:
        """Ejecuta varios experimentos (p. ej. barridos o Monte Carlo)."""
        return [self.run(exp) for exp in experiments]

    # -- Comparación ---------------------------------------------------------
    def compare(self, experiments: Iterable[Experiment]) -> pd.DataFrame:
        """Tabla comparativa de variables clave entre experimentos."""
        rows = []
        for exp in experiments:
            result = self.run(exp)
            row = {"experiment": exp.name, "model": exp.scenario.model}
            eq = result.equilibrium
            for key in ("Y", "r", "P", "e", "NX"):
                row[key] = eq.get(key)
            if result.baseline is not None and eq.get("Y") is not None:
                y0 = result.baseline.get("Y")
                if y0:
                    row["ΔY (%)"] = (eq["Y"] - y0) / y0 * 100
            rows.append(row)
        return pd.DataFrame(rows)

    def catalog(self) -> list[dict]:
        """Catálogo de modelos registrados en el motor."""
        return self.registry.info()
