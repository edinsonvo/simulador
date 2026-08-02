"""Modelos clásicos: tradicionales (cerrado/abierto) y nuevo (Lucas)."""

from .closed import ClassicalClosedModel
from .new_classical import NewClassicalModel
from .open import ClassicalOpenModel

__all__ = [
    "ClassicalClosedModel",
    "ClassicalOpenModel",
    "NewClassicalModel",
]
