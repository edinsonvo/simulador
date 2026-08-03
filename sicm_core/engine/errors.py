"""Errores de simulación y validación de parámetros.

Los mensajes se orientan al usuario final de la plataforma: explican qué
falló y qué revisar, en lugar de propagar el traceback crudo.
"""

from __future__ import annotations

import math
from dataclasses import fields


class SimulationError(RuntimeError):
    """Error de simulación con mensaje legible para el usuario."""


def validate_parameters(model_name: str, parameters) -> None:
    """Valida que los parámetros del escenario sean utilizables.

    Comprueba que todos los campos numéricos sean finitos (no ``NaN`` ni
    ``inf``). Si algo falla, lanza :class:`SimulationError` con la lista de
    parámetros problemáticos.
    """
    invalid: list[str] = []
    for f in fields(parameters):
        value = getattr(parameters, f.name)
        if value is None:
            invalid.append(f.name)
            continue
        if isinstance(value, (int, float)) and not math.isfinite(value):
            invalid.append(f.name)
    if invalid:
        names = ", ".join(sorted(invalid))
        raise SimulationError(
            f"El modelo «{model_name}» recibió parámetros no válidos "
            f"({names}). Revise los controles del escenario."
        )
