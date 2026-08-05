"""Modelos macroeconómicos.

Se importa este paquete para que los modelos queden registrados en el
registro del motor mediante el decorador :func:`sicm_core.engine.register`.
"""

from . import (
    classical,  # noqa: F401  (clásico cerrado/abierto, clásico nuevo)
    four_quadrant,  # noqa: F401  (equilibrio general de 4 cuadrantes)
    integrated,  # noqa: F401  (macromodelo de 4 planos)
    keynesian,  # noqa: F401  (IS-LM, Mundell-Fleming, OA-DA, IS-LM-BP)
    labor,  # noqa: F401  (ley de Okun, curva de Phillips)
    new_keynesian,  # noqa: F401  (3 ecuaciones neokeynesiano)
)
from .base_model import BaseModel

__all__ = ["BaseModel"]
