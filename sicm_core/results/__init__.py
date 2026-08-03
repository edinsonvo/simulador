"""Resultados de simulación: equilibrio, métricas, interpretación y transmisión."""

from .equilibrium import Equilibrium, EquilibriumResult, build_result
from .interpretation import Interpretation, build_interpretation
from .metrics import Metrics, compute_metrics
from .transmission import Transmission, build_transmission

__all__ = [
    "Equilibrium",
    "EquilibriumResult",
    "Interpretation",
    "Metrics",
    "Transmission",
    "build_interpretation",
    "build_result",
    "build_transmission",
    "compute_metrics",
]
