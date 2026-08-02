"""Registro de modelos disponibles para el motor."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from ..models.base_model import BaseModel

ModelClass = TypeVar("ModelClass", bound="BaseModel")


class ModelNotFoundError(KeyError):
    """Se lanza cuando se pide un modelo no registrado."""


class ModelRegistry:
    """Registro central de modelos.

    Los modelos se dan de alta con el decorador :func:`register`; el motor
    los descubre a través de ``get`` sin acoplar la lógica de ejecución a
    una implementación concreta.
    """

    _models: dict[str, type["BaseModel"]] = {}

    def register(self, cls: type["BaseModel"]) -> type["BaseModel"]:
        if not getattr(cls, "name", None):
            raise ValueError(f"El modelo {cls!r} debe definir 'name'.")
        self._models[cls.name] = cls
        return cls

    def get(self, name: str) -> type["BaseModel"]:
        try:
            return self._models[name]
        except KeyError:
            available = ", ".join(sorted(self._models)) or "(vacío)"
            raise ModelNotFoundError(
                f"Modelo desconocido: '{name}'. Registrados: {available}"
            ) from None

    def names(self) -> list[str]:
        return sorted(self._models)

    def labels(self) -> dict[str, str]:
        return {name: cls.label for name, cls in self._models.items()}

    def families(self) -> dict[str, list[str]]:
        groups: dict[str, list[str]] = {}
        for name, cls in self._models.items():
            groups.setdefault(cls.family, []).append(name)
        return groups

    def info(self) -> list[dict[str, Any]]:
        return [
            {"name": name, "label": cls.label, "family": cls.family}
            for name, cls in sorted(self._models.items())
        ]

    def __contains__(self, name: str) -> bool:
        return name in self._models

    def __len__(self) -> int:
        return len(self._models)


registry = ModelRegistry()


def register(cls: type["BaseModel"]) -> type["BaseModel"]:
    """Decorador para dar de alta un modelo en el registro."""
    return registry.register(cls)
