"""Modelo clásico nuevo: curva de oferta de Lucas y expectativas racionales.

El producto se desvía del natural solo ante **sorpresas** de precios:

    Oferta de Lucas:  Y = Yn·[ 1 + α·(P - Pe)/Pe ]
    Demanda agregada: M·V = P·Y

Resolviendo en términos de y = Y/Yn:

    y = 1 - α + α·M·V/(Yn·Pe·y)
      →  y² - (1 - α)·y - α·M·V/(Yn·Pe) = 0

Si la política es **anticipada** (Pe se ajusta junto con P), el equilibrio
vuelve a Y = Yn y el dinero es neutro. Si es una sorpresa (Pe fijo), el
producto se mueve temporalmente.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np

from ...engine.registry import register
from ...results.equilibrium import Equilibrium
from ..base_model import BaseModel


@register
class NewClassicalModel(BaseModel):
    """Clásico nuevo: Lucas supply + cantidad de dinero (sorpresas)."""

    name: ClassVar[str] = "new_classical"
    family: ClassVar[str] = "classical"
    label: ClassVar[str] = "Clásico nuevo (curva de Lucas, expectativas)"

    def _is_anticipated(self) -> bool:
        return str(self.scenario.metadata.get("expectativas", "sorpresa")).lower() in (
            "anticipadas",
            "racionales",
            "anticipado",
        )

    def solve(self) -> Equilibrium:
        p = self.parameters
        alpha = max(p.alpha_lucas, 0.0)
        y_natural = p.Yn
        if self._is_anticipated():
            # Expectativas racionales: P^e = P -> el dinero es neutral.
            output = y_natural
            price = p.M * p.V / max(y_natural, 1e-9)
            y_ratio = 1.0
        else:
            # Sorpresa de precios: solo el componente no anticipado mueve a Y.
            expected_price = max(p.Pe, 1e-9)
            ad = p.M * p.V / (max(y_natural, 1e-9) * expected_price)
            if alpha <= 1e-12:
                y_ratio = 1.0
            else:
                disc = (1 - alpha) ** 2 + 4 * alpha * ad
                y_ratio = ((1 - alpha) + max(np.sqrt(max(disc, 0.0)), 0.0)) / 2.0
            output = y_natural * y_ratio
            price = p.M * p.V / max(output, 1e-9)
        gap = y_ratio - 1.0
        inflation = price / max(p.P_prev, 1e-9) - 1.0
        unemployment = p.u_n - p.beta_okun * gap
        return Equilibrium(
            model=self.name,
            variables={
                "Y": float(output),
                "P": float(price),
                "gap": float(gap),
                "pi": float(inflation),
                "u": float(unemployment),
            },
        )
