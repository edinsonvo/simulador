"""Modelo clásico de economía cerrada (pleno empleo y dicotomía)."""

from __future__ import annotations

from typing import ClassVar

from ...engine.registry import register
from ...results.equilibrium import Equilibrium
from ..base_model import BaseModel

_PCT = 100.0


@register
class ClassicalClosedModel(BaseModel):
    """Economía clásica cerrada.

    Pleno empleo:     Y = Yn.
    Cantidad de dinero:  P = M·V / Yn.
    Fondos prestables:   S = I,  S = s·Y + (T - G),  I = I0 - 100·b·r.

    Implicación clave: la dicotomía clásica hace que los cambios en la
    oferta monetaria (M) alteren solo el nivel de precios (P); el producto
    y la tasa de interés reales no cambian.
    """

    name: ClassVar[str] = "classical_closed"
    family: ClassVar[str] = "classical"
    label: ClassVar[str] = "Clásico (economía cerrada)"

    def solve(self) -> Equilibrium:
        p = self.parameters
        y = p.Yn
        price = p.M * p.V / p.Yn if abs(p.Yn) > 1e-9 else float("nan")
        savings = p.s * y + (p.T - p.G)
        rate = (p.I0 - savings) / (_PCT * p.b) if abs(p.b) > 1e-9 else float("nan")
        cons = p.C0 + p.c * (y - p.T)
        inv = p.I0 - _PCT * p.b * rate
        return Equilibrium(
            model=self.name,
            variables={
                "Y": float(y),
                "P": float(price),
                "r": float(rate),
                "C": float(cons),
                "I": float(inv),
                "S": float(savings),
            },
        )
