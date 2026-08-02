"""Modelo clásico de economía abierta pequeña."""

from __future__ import annotations

from typing import ClassVar

from ...engine.registry import register
from ...results.equilibrium import Equilibrium
from ..base_model import BaseModel

_PCT = 100.0


@register
class ClassicalOpenModel(BaseModel):
    """Economía clásica abierta pequeña.

    Pleno empleo:        Y = Yn.
    Cantidad de dinero:  P = M·V / Yn.
    Paridad de tasas:    r = r_w (movilidad perfecta de capitales).
    Identidad contable:  NX = Y - C - G - I, con e = (NX0 - NX) / θ.

    El gasto público desplaza la inversión y/o las exportaciones netas
    (crowding-out) sin alterar el producto; la política monetaria solo
    cambia el nivel de precios.
    """

    name: ClassVar[str] = "classical_open"
    family: ClassVar[str] = "classical"
    label: ClassVar[str] = "Clásico (economía abierta pequeña)"

    def solve(self) -> Equilibrium:
        p = self.parameters
        y = p.Yn
        price = p.M * p.V / p.Yn if abs(p.Yn) > 1e-9 else float("nan")
        rate = p.r_w
        cons = p.C0 + p.c * (y - p.T)
        inv = p.I0 - _PCT * p.b * rate
        nx = y - cons - inv - p.G
        theta = max(p.theta, 1e-9)
        exchange = (p.NX0 - nx) / theta
        return Equilibrium(
            model=self.name,
            variables={
                "Y": float(y),
                "P": float(price),
                "r": float(rate),
                "C": float(cons),
                "I": float(inv),
                "NX": float(nx),
                "e": float(exchange),
            },
        )
