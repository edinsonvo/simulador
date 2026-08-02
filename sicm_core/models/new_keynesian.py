"""Modelo neokeynesiano de 3 ecuaciones (IS + Phillips + regla de Taylor).

Sistema simultáneo de corto plazo (versión estática de la nueva síntesis):

    IS:       x = -σ·(r - r_star) + δ_f·f     con f = (G - G_ref)/Yn, δ_f = 1/(1-c)
    Phillips: π = π_e + κ·x                    (κ = lambda_pc)
    Taylor:   r = r_star + φ·(π - π_target)    (φ = phi_taylor)

Despejando:

    π = [ π_e + κ·σ·φ·π_target + κ·δ_f·f ] / (1 + κ·σ·φ)
    x = -σ·φ·(π - π_target) + δ_f·f
    r = r_star + φ·(π - π_target)

El producto real se recupera como Y = Yn·(1 + x), el desempleo por la ley
de Okun, u = u_n - β·x, y el nivel de precios por la Phillips acumulada.
"""

from __future__ import annotations

from typing import ClassVar

from ..engine.registry import register
from ..results.equilibrium import Equilibrium
from .base_model import BaseModel


@register
class NewKeynesianModel(BaseModel):
    """Neokeynesiano: IS, curva de Phillips y regla de Taylor simultáneas."""

    name: ClassVar[str] = "new_keynesian"
    family: ClassVar[str] = "new_keynesian"
    label: ClassVar[str] = "Neokeynesiano (IS + Phillips + Taylor)"

    def _fiscal_impulse(self) -> float:
        p = self.parameters
        demand_elasticity = 1.0 / max(1 - p.c, 1e-6)
        return demand_elasticity * (p.G - p.G_ref) / max(p.Yn, 1e-9)

    def _solve_gap_inflation(self) -> tuple[float, float]:
        """Devuelve (gap x, inflación π) del sistema de 3 ecuaciones."""
        p = self.parameters
        kappa = max(p.lambda_pc, 1e-6)
        sigma_phi = p.sigma * p.phi_taylor
        demand = self._fiscal_impulse()
        numerator = p.pi_e + kappa * sigma_phi * p.pi_target + kappa * demand
        denominator = 1.0 + kappa * sigma_phi
        inflation = numerator / max(denominator, 1e-9)
        gap = -p.sigma * p.phi_taylor * (inflation - p.pi_target) + demand
        return gap, inflation

    def solve(self) -> Equilibrium:
        p = self.parameters
        gap, inflation = self._solve_gap_inflation()
        output = p.Yn * (1.0 + gap)
        rate = p.r_star + p.phi_taylor * (inflation - p.pi_target)
        unemployment = p.u_n - p.beta_okun * gap
        price = p.P_prev * (1.0 + inflation)
        return Equilibrium(
            model=self.name,
            variables={
                "Y": float(output),
                "gap": float(gap),
                "r": float(rate),
                "pi": float(inflation),
                "P": float(price),
                "u": float(unemployment),
            },
        )

    @property
    def multipliers(self) -> dict[str, float]:
        """Multiplicadores de política (fiscal G y meta de inflación)."""
        base = self.solve()["Y"]
        out: dict[str, float] = {}
        for target, delta in (("G", 1.0), ("pi_target", 0.01)):
            params = self.parameters.with_values(
                **{target: getattr(self.parameters, target) + delta}
            )
            from ..experiments.scenario import Scenario

            shocked = self.__class__(
                Scenario(model=self.name, parameters=params,
                         metadata=dict(self.scenario.metadata))
            )
            out[f"dY_d{target}"] = float(shocked.solve()["Y"] - base) / delta
        return out
