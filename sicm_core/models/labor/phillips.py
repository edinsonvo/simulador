"""Curva de Phillips aumentada por expectativas.

    gap = (Y_obs - Yn) / Yn
    π   = π_e + λ·gap

La inflación supera la esperada cuando la economía opera por encima del
pleno empleo. Se reporta además el desempleo derivado por la ley de Okun
para completar el diagnóstico del mercado laboral.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np

from ...engine.registry import register
from ...results.equilibrium import Equilibrium
from ..base_model import BaseModel


@register
class PhillipsModel(BaseModel):
    """Curva de Phillips aumentada por expectativas."""

    name: ClassVar[str] = "phillips"
    family: ClassVar[str] = "labor"
    label: ClassVar[str] = "Curva de Phillips (inflación)"

    def solve(self) -> Equilibrium:
        p = self.parameters
        gap = (p.Y_obs - p.Yn) / max(p.Yn, 1e-9)
        inflation = p.pi_e + p.lambda_pc * gap
        unemployment = p.u_n - p.beta_okun * gap
        return Equilibrium(
            model=self.name,
            variables={
                "Y": float(p.Y_obs),
                "Yn": float(p.Yn),
                "gap": float(gap),
                "pi": float(inflation),
                "u": float(unemployment),
            },
        )

    # -- Curvas para visualización --------------------------------------
    def phillips_curve(self, gap_values) -> tuple[np.ndarray, np.ndarray]:
        """Devuelve (gap, π) a lo largo de la curva de Phillips."""
        p = self.parameters
        gaps = np.asarray(gap_values, dtype=float)
        inflation = p.pi_e + p.lambda_pc * gaps
        return gaps, inflation
