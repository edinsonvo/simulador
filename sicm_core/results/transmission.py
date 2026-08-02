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
    "as_ad": [
        "Demanda agregada: IS-LM define la curva DA (Y, P).",
        "Oferta agregada: precio anclado por P_prev con pendiente λ·(Y − Yn).",
        "Equilibrio simultáneo: el par (Y, P) vacía bienes, dinero y oferta.",
        "Largo plazo: la OA se vuelve vertical en Yn y el precio ajusta.",
    ],
    "islm_bp": [
        "Mercado de bienes abierto (IS): gasto, impuestos y sector externo.",
        "Mercado de dinero (LM): saldos reales (M/P).",
        "Balance de pagos (BP): cuenta corriente y movilidad de capitales (kappa).",
        "Canal cambiario: e ajusta para equilibrar la BP (o el ancla en régimen fijo).",
    ],
    "new_keynesian": [
        "IS neokeynesiana: el gap responde a la tasa real (σ).",
        "Curva de Phillips: la inflación responde al gap (κ = lambda_pc).",
        "Regla de Taylor: el banco central reacciona a la inflación (φ).",
        "Política fiscal: impulso f = (G − G_ref)/Yn multiplicado por 1/(1 − c).",
    ],
    "new_classical": [
        "Curva de oferta de Lucas: solo las sorpresas de precios mueven el producto.",
        "Expectativas: si Pe se ajusta, la política es neutral (dinero neutro).",
        "Cantidad de dinero: M·V = P·Y determina el nivel de precios.",
        "Equilibrio: convergencia al producto natural Yn.",
    ],
    "okun": [
        "Brecha de producto: gap = (Y_obs − Yn)/Yn.",
        "Ley de Okun: u = u_n − β·gap (el desempleo es contracíclico).",
    ],
    "phillips": [
        "Brecha de producto: gap = (Y_obs − Yn)/Yn.",
        "Curva de Phillips: π = π_e + λ·gap (trade-off inflación-desempleo).",
        "Mercado laboral: desempleo derivado por la ley de Okun.",
    ],
    "integrated": [
        "Bienes + dinero + sector externo: equilibrio simultáneo IS-LM-BP (paridad).",
        "Oferta agregada y precios: DA (Y, P) cortada con el pleno empleo.",
        "Curva de Phillips: inflación según la brecha de producto.",
        "Ley de Okun: desempleo según la brecha de producto.",
        "Política: fiscal, monetaria, cambiaria y de metas de inflación.",
    ],
    "four_quadrant": [
        "Cuadrante II (IS-LM): equilibrio de bienes y dinero en el plano (Y, i).",
        "Cuadrante III (AD-AS): demanda agregada derivada de IS-LM contra la oferta agregada.",
        "Cuadrante IV (demanda de trabajo): el salario real iguala la productividad marginal.",
        "Cuadrante I (oferta de trabajo): el salario nominal y el empleo cierran el ciclo.",
        "Lazo de retroalimentación: II → Y → III → P → IV → W/P → N → I → W → II.",
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
