"""Modelos macroeconómicos.

Se importa este paquete para que los modelos queden registrados en el
registro del motor mediante el decorador :func:`sicm_core.engine.register`.
"""

from .base_model import BaseModel
from . import keynesian  # noqa: F401  (registra modelos keynesianos)
from . import classical  # noqa: F401  (registra modelos clásicos)

__all__ = ["BaseModel"]
