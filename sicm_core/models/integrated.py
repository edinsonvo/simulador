"""Macromodelo integrado: bienes, dinero, trabajo y sector externo.

Es el modelo estrella del Research Lab: resuelve en un solo sistema los
cuatro planos del análisis macroeconómico de corto plazo.

    Bienes (IS*, paridad de tasas):   (1-c)·Y = C0 - cT + I0 - 100·b·r_w + G
    Dinero (LM):                      P = M / (k·Y - h·r_w)
    BP (paridad):                     e = (m·Y - NX0) / θ,  r = r_w
    Phillips:                         π = π_e + λ·gap
    Okun:                             u = u_n - β·gap

Bajo régimen fijo el tipo de cambio se ancla en ``e_bar`` y la oferta
monetaria se vuelve endógena (M* = P·(k·Y - h·r_w)); la BP reporta la
presión que absorben las reservas.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np

from ..engine.registry import register
from ..results.equilibrium import Equilibrium
from .base_model import BaseModel

_PCT = 100.0


@register
class IntegratedModel(BaseModel):
    """Modelo integrado de 4 planos (abierto, perfecta movilidad)."""

    name: ClassVar[str] = "integrated"
    family: ClassVar[str] = "integrated"
    label: ClassVar[str] = "Modelo integrado (4 planos: IS-LM, DA-OA, Phillips, Okun)"

    def _is_fixed(self) -> bool:
        return str(self.scenario.metadata.get("regime", "Flexible")).lower() == "fijo"

    def _output(self) -> float:
        p = self.parameters
        if self._is_fixed():
            num = (
                p.C0
                - p.c * p.T
                + p.I0
                - _PCT * p.b * p.r_w
                + p.G
                + p.NX0
                + p.theta * p.e_bar
            )
            return num / max(1 - p.c + p.m, 1e-9)
        num = p.C0 - p.c * p.T + p.I0 - _PCT * p.b * p.r_w + p.G
        return num / max(1 - p.c, 1e-9)

    def _price(self, y: float) -> float:
        p = self.parameters
        money_demand = p.k * y - p.h * p.r_w
        return p.M / max(money_demand, 1e-9)

    def solve(self) -> Equilibrium:
        p = self.parameters
        y = self._output()
        price = self._price(y)
        gap = (y - p.Yn) / max(p.Yn, 1e-9)
        inflation = p.pi_e + p.lambda_pc * gap
        unemployment = p.u_n - p.beta_okun * gap
        if self._is_fixed():
            e = p.e_bar
            money = price * (p.k * y - p.h * p.r_w)
        else:
            e = (p.m * y - p.NX0) / max(p.theta, 1e-9)
            money = p.M
        nx = p.NX0 + p.theta * e - p.m * y
        cf = p.kappa * (p.r_w - p.r_w) if self._is_fixed() else 0.0
        cons = p.C0 + p.c * (y - p.T)
        inv = p.I0 - _PCT * p.b * p.r_w
        return Equilibrium(
            model=self.name,
            variables={
                "Y": float(y),
                "r": float(p.r_w),
                "P": float(price),
                "e": float(e),
                "M": float(money),
                "NX": float(nx),
                "BP": float(nx + cf),
                "gap": float(gap),
                "pi": float(inflation),
                "u": float(unemployment),
                "C": float(cons),
                "I": float(inv),
            },
        )

    @property
    def multipliers(self) -> dict[str, float]:
        """Multiplicadores de política (fiscal y monetario)."""
        base = self.solve()["Y"]
        out: dict[str, float] = {}
        for target, delta in (("G", 1.0), ("M", 1.0)):
            params = self.parameters.with_values(
                **{target: getattr(self.parameters, target) + delta}
            )
            from ..experiments.scenario import Scenario

            shocked = self.__class__(
                Scenario(
                    model=self.name,
                    parameters=params,
                    metadata=dict(self.scenario.metadata),
                )
            )
            out[f"dY_d{target}"] = float(shocked.solve()["Y"] - base) / delta
        return out

    # -- Curvas para los cuatro planos -----------------------------------
    def is_curve(self, y_values) -> tuple[np.ndarray, np.ndarray]:
        """Curva IS* en el plano (Y, r) con el BP despejado."""
        p = self.parameters
        y = np.asarray(y_values, dtype=float)
        b = max(p.b, 1e-6)
        num = p.C0 - p.c * p.T + p.I0 + p.G
        r = (num - (1 - p.c) * y) / (_PCT * b)
        return y, r

    def lm_curve(
        self, y_values, price: float | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """Curva LM* en el plano (Y, r) evaluada al nivel de precios dado."""
        p = self.parameters
        h = max(p.h, 1e-6)
        p_star = price if price is not None else self._price(self._output())
        y = np.asarray(y_values, dtype=float)
        r = (p.k * y - p.M / max(p_star, 1e-9)) / h
        return y, r

    def ad_curve(self, y_values) -> tuple[np.ndarray, np.ndarray]:
        """Demanda agregada (Y, P) con paridad de tasas."""
        p = self.parameters
        y = np.asarray(y_values, dtype=float)
        denom = np.maximum(p.k * y - p.h * p.r_w, 1e-9)
        prices = p.M / denom
        return y, prices

    def as_curve(
        self, y_values, price: float | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """Oferta agregada de corto plazo (horizontal en el precio dado)."""
        y = np.asarray(y_values, dtype=float)
        p_star = price if price is not None else self._price(self._output())
        return y, np.full_like(y, p_star)

    def phillips_curve(self, gap_values) -> tuple[np.ndarray, np.ndarray]:
        """Curva de Phillips (gap, π)."""
        p = self.parameters
        gaps = np.asarray(gap_values, dtype=float)
        return gaps, p.pi_e + p.lambda_pc * gaps

    def okun_curve(self, gap_values) -> tuple[np.ndarray, np.ndarray]:
        """Ley de Okun (gap, u)."""
        p = self.parameters
        gaps = np.asarray(gap_values, dtype=float)
        return gaps, p.u_n - p.beta_okun * gaps
