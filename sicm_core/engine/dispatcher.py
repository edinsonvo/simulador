"""Despacho de escenarios a la clase de modelo correspondiente."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .registry import ModelNotFoundError, registry

if TYPE_CHECKING:
    from ..experiments.scenario import Scenario
    from ..models.base_model import BaseModel


def get_model_class(model_name: str) -> type[BaseModel]:
    """Devuelve la clase registrada para ``model_name``."""
    return registry.get(model_name)


def dispatch(scenario: Scenario) -> BaseModel:
    """Construye la instancia de modelo adecuada para el escenario."""
    model_class = get_model_class(scenario.model)
    return model_class(scenario)


def available_models() -> list[dict]:
    """Información legible de los modelos registrados."""
    return registry.info()


def model_exists(model_name: str) -> bool:
    return model_name in registry


__all__ = [
    "ModelNotFoundError",
    "available_models",
    "dispatch",
    "get_model_class",
    "model_exists",
]
