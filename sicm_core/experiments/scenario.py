"""Parámetros económicos, choques y escenarios."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field, replace
from typing import Mapping


@dataclass(frozen=True, slots=True)
class EconomyParameters:
    """Conjunto completo de parámetros económicos.

    Campos compatibles con todos los modelos incluidos. Cada modelo
    utiliza solo el subconjunto que necesita; el resto se ignora.

    Convenciones:
    - ``Y``, ``Yn``, ``G``, ``T``, ``M``: unidades de índice (u.i.).
    - ``r``, ``r_w``: fracción (0.05 = 5 %).
    - ``P``: nivel de precios (índice, base 1.0).
    - ``kappa``: movilidad de capitales (0 = nula, ~1 = imperfecta, 1e9 = perfecta).
    """

    # Demanda interna
    C0: float = 50.0      # Consumo autónomo
    c: float = 0.75       # Propensión marginal a consumir
    I0: float = 100.0     # Inversión autónoma
    b: float = 0.4        # Sensibilidad de la inversión a r (por p.p.)
    G: float = 120.0      # Gasto del gobierno
    T: float = 80.0       # Impuestos
    # Dinero
    M: float = 350.0      # Oferta monetaria nominal
    k: float = 0.5        # Sensibilidad de la demanda de dinero a Y
    h: float = 1500.0     # Sensibilidad de la demanda de dinero a r
    P: float = 1.0        # Nivel de precios
    # Oferta / pleno empleo
    Yn: float = 1000.0    # Producto natural
    V: float = 1.0        # Velocidad del dinero
    s: float = 0.2        # Propensión al ahorro
    # Sector externo
    r_w: float = 0.05     # Tasa de interés mundial
    kappa: float = 1e9    # Movilidad de capitales
    theta: float = 0.5    # Sensibilidad de NX al tipo de cambio
    e_bar: float = 200.0  # Ancla cambiaria (régimen fijo)
    NX0: float = 30.0     # Exportaciones netas autónomas

    @classmethod
    def from_mapping(cls, data: Mapping[str, float]) -> "EconomyParameters":
        """Construye parámetros desde un mapeo (ignora claves desconocidas)."""
        allowed = set(cls.__dataclass_fields__)
        clean = {}
        for key, value in data.items():
            if key not in allowed:
                continue
            try:
                clean[key] = float(value)
            except (TypeError, ValueError):
                raise ValueError(f"El parámetro '{key}' debe ser numérico.") from None
        return cls(**clean)

    def with_values(self, **updates: float) -> "EconomyParameters":
        """Devuelve una copia con los valores indicados actualizados."""
        return replace(self, **updates)

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Shock:
    """Choque exógeno sobre un parámetro.

    ``magnitude`` se interpreta como proporción (0.10 = +10 %) salvo que
    ``absolute`` sea ``True``, en cuyo caso es un cambio en unidades.
    """

    target: str
    magnitude: float
    description: str = ""
    absolute: bool = False

    def apply_to(self, parameters: EconomyParameters) -> EconomyParameters:
        """Devuelve parámetros con el choque aplicado (sin mutar el original)."""
        current = getattr(parameters, self.target)
        if self.absolute:
            updated = current + self.magnitude
        else:
            updated = current * (1.0 + self.magnitude)
        if not math.isfinite(updated):
            raise ValueError(
                f"El choque sobre '{self.target}' produce un valor no finito."
            )
        return parameters.with_values(**{self.target: updated})


@dataclass(frozen=True, slots=True)
class Scenario:
    """Contexto económico completo de un experimento."""

    model: str
    parameters: EconomyParameters
    shocks: list[Shock] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    label: str = ""

    def with_shocks(self, *shocks: Shock) -> "Scenario":
        return replace(self, shocks=list(self.shocks) + list(shocks))


# Calibraciones por modelo (equilibrios de referencia con valores realistas).
_DEFAULTS_BY_MODEL: dict[str, dict] = {
    "islm": {
        "C0": 50.0, "c": 0.75, "I0": 100.0, "b": 0.4,
        "G": 120.0, "T": 80.0, "M": 350.0, "k": 0.5, "h": 1500.0, "P": 1.0,
    },
    "mundell_fleming": {
        "C0": 50.0, "c": 0.75, "I0": 100.0, "b": 0.4,
        "G": 120.0, "T": 80.0, "M": 200.0, "k": 0.5, "h": 1500.0, "P": 1.0,
        "r_w": 0.05, "kappa": 1e9, "theta": 0.5, "NX0": 30.0, "e_bar": 200.0,
    },
    "classical_closed": {
        "Yn": 1000.0, "C0": 50.0, "c": 0.75, "I0": 162.0, "b": 0.4,
        "G": 120.0, "T": 80.0, "s": 0.2, "M": 350.0, "V": 1.0,
    },
    "classical_open": {
        "Yn": 1000.0, "C0": 50.0, "c": 0.75, "I0": 162.0, "b": 0.4,
        "G": 120.0, "T": 80.0, "s": 0.2, "M": 350.0, "V": 1.0,
        "r_w": 0.05, "theta": 0.5, "NX0": 30.0,
    },
}

DEFAULT_MODEL = "islm"


def default_scenario(model: str, **metadata) -> Scenario:
    """Escenario con la calibración de referencia del modelo indicado."""
    overrides = _DEFAULTS_BY_MODEL.get(model, {})
    params = EconomyParameters(**overrides)
    return new_scenario(model, params, metadata=metadata or {"calibration": "default"})


def new_scenario(
    model: str,
    parameters: EconomyParameters,
    shocks: list[Shock] | None = None,
    metadata: dict | None = None,
    label: str = "",
) -> Scenario:
    return Scenario(
        model=model,
        parameters=parameters,
        shocks=list(shocks or []),
        metadata=dict(metadata or {}),
        label=label,
    )
