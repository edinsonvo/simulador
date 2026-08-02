"""Modelo IS-LM de economía cerrada (solución analítica verificada)."""

from __future__ import annotations

from typing import ClassVar

import numpy as np

from ...engine.registry import register
from ...results.equilibrium import Equilibrium
from ..base_model import BaseModel

_PCT = 100.0  # convierte sensibilidad de inversión a puntos porcentuales


@register
class ISLMModel(BaseModel):
    """IS-LM.

    Mercado de bienes (IS):  Y = C + I + G,  con  C = C0 + c(Y - T),
    I = I0 - 100·b·r.
    Mercado de dinero (LM):  M/P = k·Y - h·r.

    Ecuaciones del equilibrio general:

        Y = [h·A0 + 100·b·(M/P)] / [h(1 - c) + 100·b·k]
        r = (k·Y - M/P) / h

    con  A0 = C0 - c·T + I0 + G.
    """

    name: ClassVar[str] = "islm"
    family: ClassVar[str] = "keynesian"
    label: ClassVar[str] = "IS-LM (economía cerrada)"

    def _A0(self) -> float:
        p = self.parameters
        return p.C0 - p.c * p.T + p.I0 + p.G

    def _den(self) -> float:
        p = self.parameters
        return p.h * (1 - p.c) + _PCT * p.b * p.k

    @property
    def multipliers(self) -> dict[str, float]:
        """Multiplicadores de política del modelo.

        dY/dG: multiplicador fiscal (con reacción endógena de r).
        dY/dM: multiplicador monetario.
        """
        p = self.parameters
        den = self._den()
        if abs(den) < 1e-9:
            return {"dY_dG": 0.0, "dY_dM": 0.0}
        return {
            "dY_dG": p.h / den,
            "dY_dM": _PCT * p.b / (p.P * den),
        }

    def solve(self) -> Equilibrium:
        p = self.parameters
        den = self._den()
        if abs(den) < 1e-9:
            raise ValueError("El modelo IS-LM tiene un denominador degenerado.")
        y = (p.h * self._A0() + _PCT * p.b * p.M / p.P) / den
        r = (p.k * y - p.M / p.P) / p.h
        c_cons = p.C0 + p.c * (y - p.T)
        inv = p.I0 - _PCT * p.b * r
        return Equilibrium(
            model=self.name,
            variables={
                "Y": float(y),
                "r": float(r),
                "C": float(c_cons),
                "I": float(inv),
            },
        )

    # -- Curvas para visualización ------------------------------------------
    def is_curve(self, y_values) -> tuple[np.ndarray, np.ndarray]:
        """Devuelve (Y, r) de la curva IS."""
        p = self.parameters
        b = max(p.b, 1e-6)
        y = np.asarray(y_values, dtype=float)
        r = (self._A0() - (1 - p.c) * y) / (_PCT * b)
        return y, r

    def lm_curve(self, y_values) -> tuple[np.ndarray, np.ndarray]:
        """Devuelve (Y, r) de la curva LM."""
        p = self.parameters
        h = max(p.h, 1e-6)
        y = np.asarray(y_values, dtype=float)
        r = (p.k * y - p.M / p.P) / h
        return y, r
