"""Modelo de Oferta y Demanda Agregadas (OA-DA) de economía cerrada.

Los mercados de bienes (IS), dinero (LM) y el lado de la oferta (OA) se
resuelven **simultáneamente**: se obtiene la curva de demanda agregada a
partir del equilibrio IS-LM y se corta con la oferta agregada de corto
plazo (pendiente positiva). El resultado es un par (Y, P) y la tasa de
interés endógena.

Curva DA (del equilibrio IS-LM):

    P(Y) = M / [ k·Y - h·(A0 - (1-c)·Y) / (100·b) ]        con A0 = C0 - cT + I0 + G

Curva OA de corto plazo:

    P(Y) = P_prev · [ 1 + λ·(Y - Yn) / Yn ]
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np

from ...engine.registry import register
from ...results.equilibrium import Equilibrium
from ..base_model import BaseModel
from ..solvers import solve_1d

_PCT = 100.0


@register
class AggregateDemandSupplyModel(BaseModel):
    """OA-DA: bienes, dinero y oferta agregada resueltos a la vez."""

    name: ClassVar[str] = "as_ad"
    family: ClassVar[str] = "keynesian"
    label: ClassVar[str] = "OA-DA (oferta y demanda agregadas)"

    def _A0(self) -> float:
        p = self.parameters
        return p.C0 - p.c * p.T + p.I0 + p.G

    def ad_price(self, y: float) -> float:
        """Nivel de precios de la demanda agregada para el producto ``y``."""
        p = self.parameters
        b = max(p.b, 1e-6)
        denominator = p.k * y - p.h * (self._A0() - (1 - p.c) * y) / (_PCT * b)
        if denominator <= 1e-9:
            return float("inf")
        return p.M / denominator

    def as_price(self, y: float) -> float:
        """Nivel de precios de la oferta agregada de corto plazo."""
        p = self.parameters
        gap = (y - p.Yn) / max(p.Yn, 1e-9)
        return p.P_prev * (1.0 + p.lambda_pc * gap)

    def _residual(self, y: float) -> float:
        return self.ad_price(y) - self.as_price(y)

    def solve(self) -> Equilibrium:
        p = self.parameters
        if str(self.scenario.metadata.get("horizon", "corto")).lower() in (
            "largo",
            "pleno",
        ):
            y = p.Yn
            price = self.ad_price(y)
        else:
            y = solve_1d(self._residual, 1.0, 2.0 * max(p.Yn, 1.0))
            price = self.as_price(y)
        rate = (self._A0() - (1 - p.c) * y) / (_PCT * max(p.b, 1e-6))
        cons = p.C0 + p.c * (y - p.T)
        inv = p.I0 - _PCT * p.b * rate
        gap = (y - p.Yn) / max(p.Yn, 1e-9)
        inflation = price / max(p.P_prev, 1e-9) - 1.0
        return Equilibrium(
            model=self.name,
            variables={
                "Y": float(y),
                "P": float(price),
                "r": float(rate),
                "C": float(cons),
                "I": float(inv),
                "gap": float(gap),
                "pi": float(inflation),
            },
        )

    @property
    def multipliers(self) -> dict[str, float]:
        """Multiplicadores fiscales y monetarios (derivadas numéricas)."""

        base = self.solve()["Y"]
        out: dict[str, float] = {}
        for target, delta in (("G", 1.0), ("M", 1.0)):
            params = self.parameters.with_values(
                **{target: getattr(self.parameters, target) + delta}
            )
            from ...experiments.scenario import Scenario

            shocked = self.__class__(
                Scenario(
                    model=self.name,
                    parameters=params,
                    metadata=dict(self.scenario.metadata),
                )
            )
            out[f"dY_d{target}"] = float(shocked.solve()["Y"] - base) / delta
        return out

    # -- Curvas para visualización --------------------------------------
    def ad_curve(self, y_values) -> tuple[np.ndarray, np.ndarray]:
        """Devuelve (Y, P) de la curva de demanda agregada."""
        y = np.asarray(y_values, dtype=float)
        p = np.asarray([self.ad_price(v) for v in y], dtype=float)
        return y, p

    def as_curve(self, y_values) -> tuple[np.ndarray, np.ndarray]:
        """Devuelve (Y, P) de la curva de oferta agregada de corto plazo."""
        y = np.asarray(y_values, dtype=float)
        p = np.asarray([self.as_price(v) for v in y], dtype=float)
        return y, p
