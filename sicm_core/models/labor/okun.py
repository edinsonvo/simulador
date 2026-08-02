"""Ley de Okun: relación entre el producto observado y el desempleo.

    gap = (Y_obs - Yn) / Yn
    u   = u_n - β·gap

El coeficiente ``beta_okun`` (≈ 2) indica cuánto cae la tasa de desempleo
cuando el producto se sitúa un punto por encima de su nivel natural.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np

from ...engine.registry import register
from ...results.equilibrium import Equilibrium
from ..base_model import BaseModel


@register
class OkunModel(BaseModel):
    """Ley de Okun: producto → desempleo."""

    name: ClassVar[str] = "okun"
    family: ClassVar[str] = "labor"
    label: ClassVar[str] = "Ley de Okun (desempleo)"

    def solve(self) -> Equilibrium:
        p = self.parameters
        gap = (p.Y_obs - p.Yn) / max(p.Yn, 1e-9)
        unemployment = p.u_n - p.beta_okun * gap
        return Equilibrium(
            model=self.name,
            variables={
                "Y": float(p.Y_obs),
                "Yn": float(p.Yn),
                "gap": float(gap),
                "u": float(unemployment),
            },
        )

    # -- Curvas para visualización --------------------------------------
    def okun_curve(self, gap_values) -> tuple[np.ndarray, np.ndarray]:
        """Devuelve (gap, u) a lo largo de la ley de Okun."""
        p = self.parameters
        gaps = np.asarray(gap_values, dtype=float)
        u = p.u_n - p.beta_okun * gaps
        return gaps, u
