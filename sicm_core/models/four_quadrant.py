"""Modelo de cuatro cuadrantes: equilibrio general macroeconómico.

Los cuatro cuadrantes forman un ciclo de retroalimentación:

    II (IS-LM) --Y--> III (AD-AS) --P--> IV (laboral, W/P) --N--> I (W) --> II

- **Cuadrante II** (superior izquierdo): IS-LM en el plano (Y, i).
- **Cuadrante III** (inferior izquierdo): demanda agregada derivada de
  IS-LM y oferta agregada de corto plazo en el plano (Y, P).
- **Cuadrante IV** (inferior derecho): mercado laboral en (N, W/P), con la
  demanda de trabajo (productividad marginal, pendiente negativa) y la oferta
  de trabajo en salario real (pendiente positiva).
- **Cuadrante I** (superior derecho): mercado laboral en (N, W), con la oferta
  de trabajo en salario nominal (pendiente positiva) y la demanda de trabajo
  expresada en salario nominal (W = P·PMgL, pendiente negativa).

Cadenas de transmisión:

- Gasto:  IS -> ↑Y -> ↑P -> ↓W/P -> ↑N -> ↑W
- Dinero: LM -> ↓i -> ↑Y -> ↑P -> ↓W/P -> ↑N -> ↑W
- Productividad: AS -> ↓P -> ↑Y -> ↑W/P -> ↑N -> ↑W
- Expectativas: AS -> ↑P -> ↓Y -> ↓W/P -> ↓N -> ↓W
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np

from ..engine.registry import register
from ..results.equilibrium import Equilibrium
from .base_model import BaseModel
from .solvers import solve_1d

_PCT = 100.0


@register
class FourQuadrantModel(BaseModel):
    """Equilibrio general en cuatro cuadrantes interconectados."""

    name: ClassVar[str] = "four_quadrant"
    family: ClassVar[str] = "four_quadrant"
    label: ClassVar[str] = "Cuatro cuadrantes (equilibrio general)"

    # -- Parámetros derivados -------------------------------------------
    def _A0(self) -> float:
        p = self.parameters
        return p.C0 - p.c * p.T + p.I0 + p.G

    def _D(self) -> float:
        p = self.parameters
        return p.h * (1 - p.c) + _PCT * p.b * p.k

    def _natural_output(self) -> float:
        """Producto natural derivado de la función de producción."""
        p = self.parameters
        alpha = max(p.alpha_prod, 1e-6)
        return p.A_prod * (max(p.Nn, 1e-9) ** alpha)

    def _is_long_run(self) -> bool:
        return str(self.scenario.metadata.get("horizon", "corto")).lower() in (
            "largo",
            "pleno",
        )

    # -- Curvas de los cuadrantes ---------------------------------------
    def is_curve(self, y_values) -> tuple[np.ndarray, np.ndarray]:
        """IS: i(Y) = (A0 - (1-c)·Y) / (100·b)."""
        p = self.parameters
        y = np.asarray(y_values, dtype=float)
        b = max(p.b, 1e-6)
        r = (self._A0() - (1 - p.c) * y) / (_PCT * b)
        return y, r

    def lm_curve(
        self, y_values, price: float | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """LM: i(Y) = (k·Y - M/P) / h evaluada al nivel de precios dado."""
        p = self.parameters
        h = max(p.h, 1e-6)
        p_star = price if price is not None else self.solve()["P"]
        y = np.asarray(y_values, dtype=float)
        r = (p.k * y - p.M / max(p_star, 1e-9)) / h
        return y, r

    def ad_price(self, y: float) -> float:
        """Precio de demanda agregada (derivada de IS-LM) para el producto y."""
        p = self.parameters
        b = max(p.b, 1e-6)
        denominator = self._D() * y - p.h * self._A0()
        if denominator <= 1e-9:
            return float("inf")
        return p.M * _PCT * b / denominator

    def as_price(self, y: float) -> float:
        """Precio de oferta agregada de corto plazo."""
        p = self.parameters
        y_natural = self._natural_output()
        gap = (y - y_natural) / max(y_natural, 1e-9)
        return p.Pe * (1.0 + p.lambda_pc * gap)

    def ad_curve(self, y_values) -> tuple[np.ndarray, np.ndarray]:
        y = np.asarray(y_values, dtype=float)
        p = np.asarray([self.ad_price(v) for v in y], dtype=float)
        return y, p

    def as_curve(self, y_values) -> tuple[np.ndarray, np.ndarray]:
        y = np.asarray(y_values, dtype=float)
        p = np.asarray([self.as_price(v) for v in y], dtype=float)
        return y, p

    def labor_demand_curve(self, n_values) -> tuple[np.ndarray, np.ndarray]:
        """Demanda de trabajo (salario real): W/P = MPL = α·A·N^(α-1)."""
        p = self.parameters
        alpha = max(p.alpha_prod, 1e-6)
        n = np.asarray(n_values, dtype=float)
        w = alpha * p.A_prod * (np.maximum(n, 1e-9) ** (alpha - 1.0))
        return n, w

    def labor_demand_curve_nominal(
        self, n_values, price: float | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """Demanda de trabajo en el plano (N, W): W = P·PMgL, de pendiente
        negativa en salario nominal para un nivel de precios dado."""
        n, w_real = self.labor_demand_curve(n_values)
        p_star = price if price is not None else self.solve()["P"]
        return n, w_real * max(p_star, 1e-9)

    def labor_supply_curve(self, n_values) -> tuple[np.ndarray, np.ndarray]:
        """Oferta de trabajo (salario nominal): N^s = N0 + η·(W/P^e) ->
        W = (P^e/η)·(N - N0)."""
        p = self.parameters
        eta = max(p.eta_s, 1e-6)
        n = np.asarray(n_values, dtype=float)
        w = (p.Pe / eta) * (n - p.N0_s)
        return n, w

    def labor_supply_curve_real(
        self, n_values, price: float | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """Oferta de trabajo en el plano (N, W/P): W/P = (P^e/(P·η))·(N - N0),
        de pendiente positiva en salario real para el nivel de precios dado."""
        p = self.parameters
        eta = max(p.eta_s, 1e-6)
        p_star = price if price is not None else self.solve()["P"]
        n = np.asarray(n_values, dtype=float)
        w = (p.Pe / (max(p_star, 1e-9) * eta)) * (n - p.N0_s)
        return n, w

    def production_curve(self, n_values) -> tuple[np.ndarray, np.ndarray]:
        """Función de producción: Y = A·N^α."""
        p = self.parameters
        alpha = max(p.alpha_prod, 1e-6)
        n = np.asarray(n_values, dtype=float)
        y = p.A_prod * (np.maximum(n, 1e-9) ** alpha)
        return n, y

    # -- Resolución -------------------------------------------------------
    def _residual(self, y: float) -> float:
        return self.ad_price(y) - self.as_price(y)

    def solve(self) -> Equilibrium:
        p = self.parameters
        y_natural = self._natural_output()
        if self._is_long_run():
            y = y_natural
            price = self.ad_price(y)
        else:
            y = solve_1d(self._residual, 0.5 * y_natural, 2.0 * y_natural)
            price = self.as_price(y)
        b = max(p.b, 1e-6)
        rate = (self._A0() - (1 - p.c) * y) / (_PCT * b)
        cons = p.C0 + p.c * (y - p.T)
        inv = p.I0 - _PCT * p.b * rate
        gap = (y - y_natural) / max(y_natural, 1e-9)
        inflation = price / max(p.P_prev, 1e-9) - 1.0

        # Mercado laboral (cuadrantes IV y I)
        alpha = max(p.alpha_prod, 1e-6)
        a = max(p.A_prod, 1e-9)
        n = (y / a) ** (1.0 / alpha)
        w_real = alpha * a * (max(n, 1e-9) ** (alpha - 1.0))
        w_nom = w_real * price
        n_supply = p.N0_s + p.eta_s * (w_nom / max(p.Pe, 1e-9))
        n_demand = n
        unemployment = max(n_supply - n, 0.0)
        u_rate = unemployment / max(n_supply, 1e-9)

        return Equilibrium(
            model=self.name,
            variables={
                "Y": float(y),
                "r": float(rate),
                "P": float(price),
                "C": float(cons),
                "I": float(inv),
                "gap": float(gap),
                "pi": float(inflation),
                "N": float(n),
                "Ns": float(n_supply),
                "Nd": float(n_demand),
                "w": float(w_real),
                "W": float(w_nom),
                "U": float(unemployment),
                "u": float(u_rate),
                "Yn": float(y_natural),
                "Nn": float(p.Nn),
                "Pe": float(p.Pe),
                "A": float(a),
                "M": float(p.M),
                "G": float(p.G),
            },
        )

    @property
    def multipliers(self) -> dict[str, float]:
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

    # -- Dinámica y transmisión -------------------------------------------
    def dynamic_simulation(
        self, periods: int = 20, speed: float = 0.3
    ) -> list[Equilibrium]:
        """Camino de ajuste con expectativas adaptativas.

        Cada periodo resuelve el equilibrio de corto plazo y actualiza la
        expectativa de precios: P^e(t+1) = P^e(t) + speed·(P(t) - P^e(t)).
        Converge hacia el equilibrio de largo plazo (Y -> Yn).
        """
        from ..experiments.scenario import Scenario

        path: list[Equilibrium] = []
        pe = self.parameters.Pe
        for _ in range(periods):
            params = self.parameters.with_values(Pe=pe)
            model = self.__class__(
                Scenario(
                    model=self.name, parameters=params, metadata={"horizon": "corto"}
                )
            )
            eq = model.solve()
            path.append(eq)
            pe = pe + float(speed) * (eq["P"] - pe)
        return path


def transmission_steps(
    shock_target: str, baseline: Equilibrium, final: Equilibrium
) -> list[dict]:
    """Pasos del mecanismo de transmisión del choque entre cuadrantes.

    Devuelve una lista de ``{cuadrante, titulo, detalle, valor}`` que
    describe la cadena de efectos para el choque aplicado.
    """

    def _pct(key: str) -> str:
        b, f = baseline.get(key), final.get(key)
        if b is None or f is None or abs(b) < 1e-12:
            return f"{f:.2f}"
        return f"{f:.2f} ({100 * (f - b) / b:+.1f}%)"

    target = shock_target or ""
    if target in ("A_prod",):
        cadena = "Productividad ↑ -> la oferta agregada se desplaza a la derecha."
        cuarto_inicial = "III"
    elif target in ("Pe", "P_prev"):
        cadena = "Expectativas de precios ↑ -> la oferta agregada sube."
        cuarto_inicial = "III"
    elif target in ("M",):
        cadena = "Oferta monetaria ↑ -> la LM se desplaza a la derecha."
        cuarto_inicial = "II"
    else:
        cadena = "Gasto público ↑ -> la IS se desplaza a la derecha."
        cuarto_inicial = "II"

    cuadrantes = {
        "II": "Cuadrante II · IS-LM (Y, i)",
        "III": "Cuadrante III · AD-AS (Y, P)",
        "IV": "Cuadrante IV · Demanda de trabajo (N, W/P)",
        "I": "Cuadrante I · Oferta de trabajo (N, W)",
    }
    pasos = [
        {"cuadrante": c, "titulo": cuadrantes[c], "detalle": "", "valor": ""}
        for c in ["II", "III", "IV", "I"]
    ]
    detalle = {
        "II": (
            f"El mercado de bienes y de dinero se reequilibran: {cadena} "
            f"Producto (Y): {_pct('Y')} · Tasa (i): {_pct('r')}."
        ),
        "III": (
            "La demanda agregada (de IS-LM) se cruza con la oferta agregada: "
            f"precios (P): {_pct('P')} · brecha: {100 * final['gap']:+.1f}%."
        ),
        "IV": (
            "Con el nuevo nivel de precios, las empresas demandan trabajo según "
            f"la productividad marginal: empleo (N): {_pct('N')} · "
            f"salario real (W/P): {_pct('w')}."
        ),
        "I": (
            "El salario nominal se ajusta a la oferta de trabajo: "
            f"salario nominal (W): {_pct('W')} · "
            f"desempleo (U): {final['U']:.1f} ({final['u'] * 100:.1f}%)."
        ),
    }
    for paso in pasos:
        paso["detalle"] = detalle[paso["cuadrante"]]
        if paso["cuadrante"] == cuarto_inicial:
            paso["valor"] = "origen"
    return pasos
