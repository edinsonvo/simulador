"""Canales de transmisión de un choque según el modelo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..experiments.scenario import Shock

CHANNELS_BY_MODEL: dict[str, list[str]] = {
    "islm": [
        "Mercado de bienes (IS): multiplicador del gasto y efecto impuestos.",
        "Mercado de dinero (LM): saldos reales (M/P).",
        "Canal de la tasa de interés: inversión sensible a r.",
        "Efecto crowding-out: la suba de r expulsa inversión privada.",
    ],
    "mundell_fleming": [
        "Mercado de bienes abierto (IS*): gasto y sector externo.",
        "Mercado de dinero (LM*): saldos reales con r = f(r_w).",
        "Canal cambiario: tipo de cambio nominal (e) y competitividad.",
        "Balance de pagos: flujos de capital según movilidad (kappa).",
    ],
    "classical_closed": [
        "Dicotomía clásica: neutralidad del dinero (M afecta solo a P).",
        "Cantidad de dinero: M·V = P·Y fija el nivel de precios.",
        "Fondos prestables: el ahorro (s·Y + T − G) equilibra la inversión.",
    ],
    "classical_open": [
        "Dicotomía clásica: neutralidad del dinero.",
        "Paridad de tasas: r = r_w en una economía abierta pequeña.",
        "Tipo de cambio real: competitividad y exportaciones netas.",
    ],
}


@dataclass(frozen=True, slots=True)
class Transmission:
    """Canales por los que el choque se propaga a la economía."""

    channels: list[str]
    description: str


def build_transmission(model_name: str, shocks: list["Shock"]) -> Transmission:
    """Describe los canales de transmisión relevantes para el modelo."""
    channels = list(CHANNELS_BY_MODEL.get(model_name, []))
    if shocks:
        target = shocks[0].target
        if target == "r_w":
            channels.append("Choque externo: cambio en la tasa mundial (r_w).")
        elif target == "Yn":
            channels.append("Choque de oferta: cambio en el producto natural (Yn).")
    description = (
        "La propagación del choque sigue la estructura de mercado del modelo: "
        "los mercados se reequilibran y los efectos reales dependen del grado "
        "de flexibilidad de precios y de la movilidad internacional del capital."
    )
    return Transmission(channels=channels, description=description)
