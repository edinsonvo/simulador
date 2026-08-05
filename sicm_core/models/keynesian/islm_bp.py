"""Modelo IS-LM-BP: economía abierta con movilidad de capitales imperfecta.

Resuelve **simultáneamente** el mercado de bienes abierto, el mercado de
dinero y la balanza de pagos para (Y, r, e):

    IS:   (1 - c + m)·Y = C0 - c·T + I0 - 100·b·r + G + NX0 + θ·e
    LM:   M/P = k·Y - h·r
    BP:   NX0 + θ·e - m·Y + κ·(r - r_w) = 0

Con movilidad imperfecta (``kappa`` finito) la BP es creciente en (Y, r):
un mayor producto deteriora la cuenta corriente y exige una tasa más alta
para atraer capitales. Bajo régimen fijo el tipo de cambio se ancla en
``e_bar`` y el sistema resuelve (Y, r); la BP reporta la presión que
absorben las reservas.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np

from ...engine.registry import register
from ...results.equilibrium import Equilibrium
from ..base_model import BaseModel
from ..solvers import solve_system

_PCT = 100.0


@register
class ISLMBPModel(BaseModel):
    """IS-LM-BP con movilidad de capitales (imperfecta) y régimen cambiario."""

    name: ClassVar[str] = "islm_bp"
    family: ClassVar[str] = "keynesian"
    label: ClassVar[str] = "IS-LM-BP (economía abierta, movilidad imperfecta)"

    def _is_fixed(self) -> bool:
        return str(self.scenario.metadata.get("regime", "Flexible")).lower() == "fijo"

    # -- Ecuaciones ------------------------------------------------------
    def _goods_residual(self, y, r, e) -> float:
        p = self.parameters
        lhs = (1 - p.c + p.m) * y
        rhs = p.C0 - p.c * p.T + p.I0 - _PCT * p.b * r + p.G + p.NX0 + p.theta * e
        return lhs - rhs

    def _money_residual(self, y, r, e) -> float:
        p = self.parameters
        return p.M / max(p.P, 1e-9) - (p.k * y - p.h * r)

    def _bp_residual(self, y, r, e) -> float:
        p = self.parameters
        return p.NX0 + p.theta * e - p.m * y + p.kappa * (r - p.r_w)

    def _system(self, x):
        y, r, e = x
        return np.asarray(
            [
                self._goods_residual(y, r, e),
                self._money_residual(y, r, e),
                self._bp_residual(y, r, e),
            ]
        )

    def solve(self) -> Equilibrium:
        p = self.parameters
        if self._is_fixed():
            e = p.e_bar

            def _fixed(x):
                y, r = x
                return np.asarray(
                    [
                        self._goods_residual(y, r, e),
                        self._money_residual(y, r, e),
                    ]
                )

            y, r = solve_system(_fixed, np.asarray([p.Yn, p.r_w]))
        else:
            y, r, e = solve_system(
                self._system,
                np.asarray([p.Yn, p.r_w, p.e_bar]),
            )
        rate = float(r)
        cons = p.C0 + p.c * (y - p.T)
        inv = p.I0 - _PCT * p.b * rate
        nx = p.NX0 + p.theta * e - p.m * y
        cf = p.kappa * (rate - p.r_w)
        bp = nx + cf
        return Equilibrium(
            model=self.name,
            variables={
                "Y": float(y),
                "r": float(rate),
                "e": float(e),
                "C": float(cons),
                "I": float(inv),
                "NX": float(nx),
                "CF": float(cf),
                "BP": float(bp),
            },
        )

    # -- Curvas para visualización (plano Y, r) --------------------------
    def is_curve(self, y_values) -> tuple[np.ndarray, np.ndarray]:
        p = self.parameters
        y = np.asarray(y_values, dtype=float)
        b = max(p.b, 1e-6)
        num = p.C0 - p.c * p.T + p.I0 + p.G + p.NX0 + p.theta * p.e_bar
        r = (num - (1 - p.c + p.m) * y) / (_PCT * b)
        return y, r

    def lm_curve(self, y_values) -> tuple[np.ndarray, np.ndarray]:
        p = self.parameters
        h = max(p.h, 1e-6)
        y = np.asarray(y_values, dtype=float)
        r = (p.k * y - p.M / max(p.P, 1e-9)) / h
        return y, r

    def bp_curve(self, y_values) -> tuple[np.ndarray, np.ndarray]:
        p = self.parameters
        kappa = max(p.kappa, 1e-6)
        y = np.asarray(y_values, dtype=float)
        r = p.r_w + (p.m * y - p.NX0 - p.theta * p.e_bar) / kappa
        return y, r
