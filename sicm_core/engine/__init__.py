"""Motor de SICM: registro, despacho y ejecución de experimentos."""

from .dispatcher import available_models, dispatch, get_model_class, model_exists
from .engine import Engine
from .registry import ModelNotFoundError, ModelRegistry, register, registry

__all__ = [
    "Engine",
    "ModelNotFoundError",
    "ModelRegistry",
    "available_models",
    "dispatch",
    "get_model_class",
    "model_exists",
    "register",
    "registry",
]
