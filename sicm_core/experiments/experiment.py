"""Experimentos: la unidad de trabajo del motor."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from ..results.equilibrium import EquilibriumResult
    from .scenario import Scenario

_PENDING = "pending"


@dataclass(slots=True)
class Experiment:
    """Un experimento ejecuta un escenario a través del motor.

    El motor rellena :attr:`result` y cambia :attr:`status` a
    ``completed`` (o ``failed``) al ejecutarse.
    """

    id: UUID
    scenario: Scenario
    name: str
    description: str = ""
    author: str = "SICM Core"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    result: EquilibriumResult | None = None
    notes: str = ""
    status: str = _PENDING


def new_experiment(
    name: str,
    scenario: Scenario,
    description: str = "",
    author: str = "SICM Core",
    notes: str = "",
) -> Experiment:
    """Crea un experimento con identificador y fecha automáticos."""
    return Experiment(
        id=uuid4(),
        name=name,
        description=description,
        author=author,
        created_at=datetime.now(UTC),
        scenario=scenario,
        notes=notes,
    )
