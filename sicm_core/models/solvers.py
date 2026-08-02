"""Utilidades numéricas para resolver sistemas simultáneos."""

from __future__ import annotations

from typing import Callable

import numpy as np

from scipy.optimize import brentq, fsolve


def solve_1d(func: Callable[[float], float], lo: float, hi: float,
             n: int = 300) -> float:
    """Raíz de ``func`` en [lo, hi] con búsqueda robusta de la banda."""
    samples = np.linspace(float(lo), float(hi), n)
    values = np.asarray([func(x) for x in samples], dtype=float)
    for i in range(len(values) - 1):
        a, b = samples[i], samples[i + 1]
        fa, fb = values[i], values[i + 1]
        if not (np.isfinite(fa) and np.isfinite(fb)):
            continue
        if fa * fb <= 0.0:
            return float(brentq(func, a, b, xtol=1e-10))
    raise ValueError(
        f"No se encontró raíz de la función en [{lo:g}, {hi:g}]."
    )


def solve_system(funcs: Callable[[np.ndarray], np.ndarray],
                 x0: np.ndarray) -> np.ndarray:
    """Resuelve ``funcs(x) = 0`` probando varios arranques (Newton robusto)."""
    x0 = np.asarray(x0, dtype=float)
    starts = [
        x0,
        x0 * 1.1,
        x0 * 0.9,
        x0 + np.full_like(x0, 0.01),
        x0 - np.full_like(x0, 0.01),
    ]
    for start in starts:
        sol, info, ier, _ = fsolve(funcs, start, full_output=True, xtol=1e-10)
        if ier == 1 and np.all(np.isfinite(sol)):
            return np.asarray(sol, dtype=float)
    raise ValueError("No convergió el sistema de ecuaciones simultáneas.")


def feasible(f: float) -> bool:
    """Verifica que un valor sea finito y utilizable."""
    return bool(np.isfinite(f))
