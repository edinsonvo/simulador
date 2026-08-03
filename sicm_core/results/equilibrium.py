"""Equilibrio económico y resultado completo de una simulación."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..experiments.scenario import Shock
    from ..models.base_model import BaseModel
    from .interpretation import Interpretation
    from .metrics import Metrics
    from .transmission import Transmission

_EPS = 1e-12


@dataclass(frozen=True, slots=True)
class Equilibrium:
    """Punto de equilibrio de un modelo: variables endógenas.

    ``model`` identifica el modelo y ``variables`` es un mapeo
    nombre → valor (p. ej. ``{"Y": 833.0, "r": 0.044}``). Los valores
    siguen las convenciones del paquete: ``Y`` en unidades de índice,
    ``r`` como fracción (0.05 = 5 %).
    """

    model: str
    variables: Mapping[str, float]
    label: str = "equilibrio"

    def __getitem__(self, key: str) -> float:
        return self.variables[key]

    def get(self, key: str, default: float | None = None) -> float | None:
        return self.variables.get(key, default)

    def __getattr__(self, name: str) -> float:
        """Acceso por atributo: ``eq.Y`` equivale a ``eq[\"Y\"]``."""
        try:
            return self.variables[name]
        except KeyError:
            raise AttributeError(name) from None

    def as_dict(self) -> dict[str, float]:
        return dict(self.variables)

    def keys(self) -> tuple[str, ...]:
        return tuple(self.variables.keys())

    def items(self):
        return self.variables.items()

    def __iter__(self):
        return iter(self.variables)

    def __len__(self) -> int:
        return len(self.variables)

    def diff(self, other: Equilibrium) -> dict[str, float]:
        """Cambios absolutos ``other - self`` para variables compartidas."""
        return {
            k: float(other.variables[k]) - float(self.variables[k])
            for k in self.variables
            if k in other.variables
        }

    def rel_diff(self, other: Equilibrium) -> dict[str, float]:
        """Cambios relativos ``(other - self) / self`` para variables compartidas."""
        out: dict[str, float] = {}
        for k in self.variables:
            if k not in other.variables or abs(self.variables[k]) < _EPS:
                continue
            out[k] = (float(other.variables[k]) - float(self.variables[k])) / float(
                self.variables[k]
            )
        return out


@dataclass(slots=True)
class EquilibriumResult:
    """Resultado completo de un experimento.

    - ``equilibrium``: estado final (tras aplicar los choques).
    - ``baseline``: estado de referencia (sin choques).
    - ``metrics``: variaciones y multiplicadores.
    - ``interpretation``: lectura económica en lenguaje natural.
    - ``transmission``: canales de transmisión del choque.
    - ``plots``: identificadores de las figuras generadas.
    """

    equilibrium: Equilibrium
    metrics: Metrics
    interpretation: Interpretation
    transmission: Transmission
    plots: list[str] = field(default_factory=list)
    baseline: Equilibrium | None = None
    shocks: list[Shock] = field(default_factory=list)

    def variable_table(self) -> dict[str, dict[str, Any]]:
        """Tabla comparativa variable → {base, final, delta}."""
        if self.baseline is None:
            base = {}
        else:
            base = self.baseline.variables
        table: dict[str, dict[str, Any]] = {}
        for k, v in self.equilibrium.variables.items():
            table[k] = {
                "base": base.get(k),
                "final": v,
                "delta": None if k not in base else v - base[k],
            }
        return table


def build_result(
    model: BaseModel,
    baseline: Equilibrium,
    final: Equilibrium,
    shocks: list[Shock],
) -> EquilibriumResult:
    """Ensambla un :class:`EquilibriumResult` a partir de los equilibrios."""
    from .interpretation import build_interpretation
    from .metrics import compute_metrics
    from .transmission import build_transmission

    metrics = compute_metrics(baseline, final, shocks, model.parameters.as_dict())
    interpretation = build_interpretation(model, baseline, final, shocks)
    transmission = build_transmission(model.name, shocks)
    return EquilibriumResult(
        equilibrium=final,
        baseline=baseline,
        shocks=list(shocks),
        metrics=metrics,
        interpretation=interpretation,
        transmission=transmission,
    )
