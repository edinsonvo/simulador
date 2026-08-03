"""Simulación de políticas económicas."""

from __future__ import annotations

from dataclasses import dataclass

from ..experiments.scenario import Scenario, Shock


@dataclass(frozen=True, slots=True)
class Policy:
    """Descripción de una política económica."""

    name: str
    target: str
    sign: float
    description: str

    def to_shock(self, magnitude: float = 0.10) -> Shock:
        return Shock(
            target=self.target,
            magnitude=self.sign * magnitude,
            description=self.description,
        )


# Catálogo de políticas aplicables a todos los modelos.
POLICIES: dict[str, Policy] = {
    "fiscal_expansion": Policy(
        "fiscal_expansion", "G", +1.0, "Política fiscal expansiva (gasto ↑)"
    ),
    "fiscal_contraction": Policy(
        "fiscal_contraction", "G", -1.0, "Política fiscal contractiva (gasto ↓)"
    ),
    "monetary_expansion": Policy(
        "monetary_expansion", "M", +1.0, "Política monetaria expansiva (M ↑)"
    ),
    "monetary_contraction": Policy(
        "monetary_contraction", "M", -1.0, "Política monetaria contractiva (M ↓)"
    ),
}

POLICY_NAMES: list[str] = list(POLICIES.keys())


def available_policies() -> list[Policy]:
    return list(POLICIES.values())


def policy_shock(policy: str, magnitude: float = 0.10) -> Shock:
    """Instancia el choque correspondiente a una política."""
    if policy not in POLICIES:
        raise KeyError(
            f"Política desconocida: '{policy}'. Válidas: {', '.join(POLICY_NAMES)}"
        )
    return POLICIES[policy].to_shock(magnitude)


def policy_description(policy: str) -> str:
    return POLICIES[policy].description


def simulate_policy(scenario: Scenario, policy: str, magnitude: float = 0.10) -> Scenario:
    """Devuelve un escenario con la política aplicada como choque."""
    return scenario.with_shocks(policy_shock(policy, magnitude))
