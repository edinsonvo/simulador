"""Metadatos de experimentos y del entorno de ejecución."""

from __future__ import annotations

import platform
from dataclasses import asdict, dataclass, field

from .. import __version__


@dataclass(frozen=True, slots=True)
class ExperimentMetadata:
    """Información de contexto de un experimento."""

    version: str = __version__
    framework: str = "sicm_core"
    python_version: str = field(default_factory=lambda: platform.python_version())
    runtime_seconds: float | None = None

    def as_dict(self) -> dict:
        return asdict(self)


def new_metadata(runtime_seconds: float | None = None) -> ExperimentMetadata:
    return ExperimentMetadata(runtime_seconds=runtime_seconds)
