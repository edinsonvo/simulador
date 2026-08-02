"""Motor de SICM: registro, despacho y ejecución de experimentos."""

from .registry import ModelRegistry, ModelNotFoundError, register, registry
from .dispatcher import dispatch, get_model_class, available_models, model_exists
from .engine import Engine

__all__ = [
    "ModelRegistry",
    "ModelNotFoundError",
    "register",
    "registry",
    "dispatch",
    "get_model_class",
    "available_models",
    "model_exists",
    "Engine",
]
