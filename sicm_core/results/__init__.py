"""Resultados de simulación: equilibrio, métricas, interpretación y transmisión."""

from .equilibrium import Equilibrium, EquilibriumResult, build_result
from .metrics import Metrics, compute_metrics
from .interpretation import Interpretation, build_interpretation
from .transmission import Transmission, build_transmission

__all__ = [
    "Equilibrium",
    "EquilibriumResult",
    "build_result",
    "Metrics",
    "compute_metrics",
    "Interpretation",
    "build_interpretation",
    "Transmission",
    "build_transmission",
]
