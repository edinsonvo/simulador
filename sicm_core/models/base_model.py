"""Clase base de todos los modelos económicos."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from ..experiments.scenario import Scenario, Shock
    from ..results.equilibrium import Equilibrium


class BaseModel(ABC):
    """Interfaz común de un modelo económico.

    Un modelo recibe un :class:`Scenario`, resuelve su equilibrio y puede
    resolver de nuevo tras aplicar una lista de choques.
    """

    name: ClassVar[str] = "base"
    family: ClassVar[str] = "generic"
    label: ClassVar[str] = "Modelo base"

    def __init__(self, scenario: "Scenario") -> None:
        self.scenario = scenario

    @property
    def parameters(self):
        return self.scenario.parameters

    @abstractmethod
    def solve(self) -> "Equilibrium":
        """Resuelve el equilibrio del escenario y lo devuelve."""

    def solve_with_shocks(
        self, shocks: list["Shock"]
    ) -> tuple["Equilibrium", "Equilibrium"]:
        """Resuelve el equilibrio base y el equilibrio con choques aplicados.

        Devuelve ``(baseline, final)``. No muta el escenario original.
        """
        from ..analysis.shocks import apply_shocks
        from ..experiments.scenario import Scenario

        shocked_params, _ = apply_shocks(self.parameters, shocks)
        shocked_scenario = Scenario(
            model=self.scenario.model,
            parameters=shocked_params,
            shocks=list(self.scenario.shocks) + list(shocks),
            metadata=dict(self.scenario.metadata),
            label=self.scenario.label,
        )
        final_model = self.__class__(shocked_scenario)
        return self.solve(), final_model.solve()
