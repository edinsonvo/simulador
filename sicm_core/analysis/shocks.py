"""Catálogo de choques estándar y utilidades de aplicación."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from ..experiments.scenario import EconomyParameters, Shock

# Definición declarativa de choques por modelo.
# (target, magnitude, description)
_SHOCK_SPECS: dict[str, list[tuple[str, float, str]]] = {
    "islm": [
        ("G", +0.10, "aumento del gasto público (+10%)"),
        ("G", -0.10, "reducción del gasto público (-10%)"),
        ("T", -0.10, "reducción de impuestos (-10%)"),
        ("T", +0.10, "aumento de impuestos (+10%)"),
        ("M", +0.10, "expansión de la oferta monetaria (+10%)"),
        ("M", -0.10, "contracción de la oferta monetaria (-10%)"),
    ],
    "mundell_fleming": [
        ("G", +0.10, "aumento del gasto público (+10%)"),
        ("G", -0.10, "reducción del gasto público (-10%)"),
        ("M", +0.10, "expansión de la oferta monetaria (+10%)"),
        ("M", -0.10, "contracción de la oferta monetaria (-10%)"),
        ("r_w", +0.10, "aumento de la tasa mundial (+10%)"),
        ("r_w", -0.10, "reducción de la tasa mundial (-10%)"),
    ],
    "classical_closed": [
        ("M", +0.10, "expansión de la oferta monetaria (+10%)"),
        ("M", -0.10, "contracción de la oferta monetaria (-10%)"),
        ("G", +0.10, "aumento del gasto público (+10%)"),
        ("Yn", +0.05, "aumento del producto natural (+5%)"),
    ],
    "classical_open": [
        ("M", +0.10, "expansión de la oferta monetaria (+10%)"),
        ("G", +0.10, "aumento del gasto público (+10%)"),
        ("r_w", +0.10, "aumento de la tasa mundial (+10%)"),
        ("Yn", +0.05, "aumento del producto natural (+5%)"),
    ],
}


@dataclass(frozen=True, slots=True)
class ShockSpec:
    """Especificación declarativa de un choque del catálogo."""

    target: str
    magnitude: float
    description: str


SHOCK_CATALOG: dict[str, list[ShockSpec]] = {
    model: [ShockSpec(*spec) for spec in specs]
    for model, specs in _SHOCK_SPECS.items()
}


def shocks_for(model_name: str) -> list[Shock]:
    """Instancias :class:`Shock` del catálogo para el modelo indicado."""
    return [
        Shock(target=spec.target, magnitude=spec.magnitude, description=spec.description)
        for spec in SHOCK_CATALOG.get(model_name, [])
    ]


def apply_shock(parameters: EconomyParameters, shock: Shock) -> EconomyParameters:
    """Aplica un único choque sobre una copia de los parámetros."""
    return shock.apply_to(parameters)


def apply_shocks(
    parameters: EconomyParameters, shocks: list[Shock]
) -> tuple[EconomyParameters, list[Shock]]:
    """Aplica una lista de choques en orden sobre una copia de los parámetros."""
    result = parameters
    for shock in shocks:
        result = shock.apply_to(result)
    return result, list(shocks)


def validate_target(parameters: Mapping[str, float], target: str) -> bool:
    """Verifica que ``target`` sea un parámetro válido."""
    return target in EconomyParameters.__dataclass_fields__
