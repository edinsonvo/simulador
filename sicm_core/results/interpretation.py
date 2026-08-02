"""Interpretación económica en lenguaje natural de un resultado."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..experiments.scenario import Shock
    from ..models.base_model import BaseModel
    from .equilibrium import Equilibrium

_EPS = 1e-12


@dataclass(frozen=True, slots=True)
class Interpretation:
    """Lectura económica del resultado de un experimento."""

    title: str
    summary: str
    bullets: list[str]
    direction: str  # "expansivo" | "contractivo" | "neutro"


def _fmt(value: float, nd: int = 2) -> str:
    return f"{value:,.{nd}f}"


def _shock_desc(shocks: list["Shock"]) -> str:
    if not shocks:
        return ""
    first = shocks[0]
    if first.description:
        return first.description
    sign = "+" if first.magnitude > 0 else ""
    op = "aumento" if first.magnitude > 0 else "reducción"
    if first.absolute:
        return f"{op} de {first.target} en {sign}{first.magnitude:.0f} unidades"
    return f"{op} de {first.target} en {sign}{first.magnitude * 100:.0f}%"


def _build_bullets(
    baseline: "Equilibrium", final: "Equilibrium"
) -> list[str]:
    bullets: list[str] = []
    y0, y1 = baseline.get("Y"), final.get("Y")
    if y0 is not None and y1 is not None:
        pct = (y1 - y0) / y0 * 100 if abs(y0) > _EPS else 0.0
        bullets.append(f"Producto (Y): {_fmt(y0)} → {_fmt(y1)} ({pct:+.2f}%).")
    for var, label in (
        ("r", "Tasa de interés (r)"),
        ("P", "Nivel de precios (P)"),
        ("e", "Tipo de cambio (e)"),
        ("NX", "Exportaciones netas (NX)"),
    ):
        b, f = baseline.get(var), final.get(var)
        if b is None or f is None:
            continue
        if var == "r":
            bullets.append(
                f"{label}: {_fmt(b * 100)}% → {_fmt(f * 100)}% "
                f"({(f - b) * 100:+.2f} p.p.)."
            )
        else:
            base = b if abs(b) > _EPS else 1.0
            bullets.append(
                f"{label}: {_fmt(b)} → {_fmt(f)} ({(f - b) / base * 100:+.2f}%)."
            )
    return bullets


def _build_summary(
    family: str,
    direction: str,
    shock_desc: str,
    baseline: "Equilibrium",
    final: "Equilibrium",
) -> str:
    y0, y1 = baseline.get("Y"), final.get("Y")
    y_part = "el producto"
    if y0 is not None and y1 is not None and abs(y0) > _EPS:
        y_part = f"el producto en {(y1 - y0) / y0 * 100:+.2f}%"
    if family == "classical":
        return (
            "Modelo clásico: opera en pleno empleo (Y = Yn). "
            "La dicotomía clásica separa el lado real del monetario: "
            f"los cambios en la oferta monetaria afectan solo al nivel de "
            f"precios y dejan inalterados el producto real y la tasa real. "
            f"El choque descrito ({shock_desc or '—'}) mueve {y_part}."
        )
    return (
        "La economía ajusta el mercado de bienes y el de dinero "
        "simultáneamente. "
        f"El choque ({shock_desc or '—'}) es de carácter {direction}: "
        f"desplaza {y_part} y reasigna la composición del gasto "
        "(consumo, inversión, gasto público y, en economías abiertas, "
        "el sector externo)."
    )


def build_interpretation(
    model: "BaseModel",
    baseline: "Equilibrium",
    final: "Equilibrium",
    shocks: list["Shock"],
) -> Interpretation:
    """Genera la interpretación del resultado del experimento."""
    y0, y1 = baseline.get("Y"), final.get("Y")
    if y0 is not None and y1 is not None and abs(y1 - y0) > _EPS:
        direction = "expansivo" if y1 > y0 else "contractivo"
    else:
        direction = "neutro"

    shock_desc = _shock_desc(shocks)
    if shock_desc:
        title = f"{model.label}: efecto de {shock_desc}"
    else:
        title = f"{model.label}: equilibrio de referencia"

    summary = _build_summary(model.family, direction, shock_desc, baseline, final)
    bullets = _build_bullets(baseline, final)
    return Interpretation(
        title=title,
        summary=summary,
        bullets=bullets,
        direction=direction,
    )
