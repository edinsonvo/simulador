"""Modelo Mundell-Fleming de economía abierta pequeña (solución analítica)."""

from __future__ import annotations

from typing import ClassVar

import numpy as np

from ...engine.registry import register
from ...results.equilibrium import Equilibrium
from ..base_model import BaseModel

_PCT = 100.0


@register
class MundellFlemingModel(BaseModel):
    """Mundell-Fleming en el plano (Y, e) con régimen cambiario.

    IS*:  Y = C + I + G + NX,   con  C = C0 + c(Y - T),
          I = I0 - 100·b·r_w,   NX = NX0 - θ·e.
    LM*:  M/P = k·Y - h·r_w.

    El régimen se lee de ``scenario.metadata["regime"]`` ("Flexible" por
    defecto o "Fijo"). Bajo el régimen flexible la tasa doméstica iguala la
    mundial (movilidad de capitales) y la oferta monetaria es exógena; bajo
    el régimen fijo el tipo de cambio se fija en ``e_bar`` y la oferta
    monetaria se vuelve endógena para sostener el ancla.

    ``kappa`` (movilidad de capitales) no altera el equilibrio en el plano
    (Y, e) — es la presentación IS*/LM* estándar —, pero sí aparece en los
    indicadores de balanza de pagos reportados (NX, CF, BP).
    """

    name: ClassVar[str] = "mundell_fleming"
    family: ClassVar[str] = "keynesian"
    label: ClassVar[str] = "Mundell-Fleming (economía abierta pequeña)"

    def _is_fixed(self) -> bool:
        return str(self.scenario.metadata.get("regime", "Flexible")).lower() == "fijo"

    def solve(self) -> Equilibrium:
        p = self.parameters
        r_w = p.r_w
        if self._is_fixed():
            nx = p.NX0 - p.theta * p.e_bar
            num = p.C0 - p.c * p.T + p.I0 - _PCT * p.b * r_w + p.G + p.NX0
            y = (num - p.theta * p.e_bar) / (1 - p.c)
            money = p.P * (p.k * y - p.h * r_w)
            e = p.e_bar
        else:
            y = (p.M / p.P + p.h * r_w) / p.k
            num = p.C0 - p.c * p.T + p.I0 - _PCT * p.b * r_w + p.G + p.NX0
            e = (num - (1 - p.c) * y) / p.theta
            money = p.M
        nx = p.NX0 - p.theta * e
        cf = 0.0  # tasa doméstica = tasa mundial ⇒ flujo de capital neto nulo
        return Equilibrium(
            model=self.name,
            variables={
                "Y": float(y),
                "r": float(r_w),
                "e": float(e),
                "M": float(money),
                "NX": float(nx),
                "CF": float(cf),
                "BP": float(nx + cf),
            },
        )

    # -- Curvas para visualización ------------------------------------------
    def is_curve(self, y_values) -> tuple[np.ndarray, np.ndarray]:
        """Devuelve (Y, e) de la curva IS*."""
        p = self.parameters
        theta = max(p.theta, 1e-6)
        y = np.asarray(y_values, dtype=float)
        num = p.C0 - p.c * p.T + p.I0 - _PCT * p.b * p.r_w + p.G + p.NX0
        e = (num - (1 - p.c) * y) / theta
        return y, e

    def lm_curve(self, y_values) -> tuple[np.ndarray, np.ndarray]:
        """Devuelve (Y, e) de la curva LM* (vertical en el plano (Y, e))."""
        p = self.parameters
        y_eq = (p.M / p.P + p.h * p.r_w) / p.k
        y = np.asarray(y_values, dtype=float)
        return y, np.full_like(y, y_eq)
