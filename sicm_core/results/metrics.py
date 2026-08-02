"""Métricas cuantitativas de una simulación."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping

if TYPE_CHECKING:
    from ..experiments.scenario import Shock
    from .equilibrium import Equilibrium

_EPS = 1e-12


@dataclass(frozen=True, slots=True)
class Metrics:
    """Conjunto de métricas derivadas de un par de equilibrios.

    - ``deltas``: cambios absolutos por variable endógena.
    - ``relative_changes``: cambios relativos por variable endógena.
    - ``multipliers``: multiplicadores ``d<var>/d<target>`` de política.
    """

    deltas: dict[str, float]
    relative_changes: dict[str, float]
    multipliers: dict[str, float]

    def as_dict(self) -> dict[str, dict[str, float]]:
        return {
            "deltas": dict(self.deltas),
            "relative_changes": dict(self.relative_changes),
            "multipliers": dict(self.multipliers),
        }


def compute_metrics(
    baseline: "Equilibrium",
    final: "Equilibrium",
    shocks: list["Shock"],
    params_before: Mapping[str, float],
) -> Metrics:
    """Calcula deltas, cambios relativos y multiplicadores.

    El multiplicador ``dY/dG`` se define como el cambio del producto entre
    el cambio absoluto del parámetro objetivo del choque.
    """
    deltas = baseline.diff(final)
    relative = baseline.rel_diff(final)

    multipliers: dict[str, float] = {}
    for shock in shocks:
        target = shock.target
        if target not in params_before:
            continue
        if shock.absolute:
            dx = shock.magnitude
        else:
            dx = params_before[target] * shock.magnitude
        if abs(dx) < _EPS:
            continue
        for var in ("Y", "P", "r", "e", "NX"):
            if baseline.get(var) is None or final.get(var) is None:
                continue
            dvar = float(final[var]) - float(baseline[var])
            multipliers[f"d{var}_d{target}"] = dvar / dx
    return Metrics(deltas=deltas, relative_changes=relative, multipliers=multipliers)
