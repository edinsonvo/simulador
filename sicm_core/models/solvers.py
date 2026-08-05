"""Utilidades numéricas para resolver sistemas simultáneos."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from scipy.optimize import brentq, fsolve, minimize_scalar


def solve_1d(func: Callable[[float], float], lo: float, hi: float, n: int = 300) -> float:
    """Raíz de ``func`` en [lo, hi] con búsqueda robusta de la banda.

    Estrategia:
    1. Barrer ``n`` puntos en [lo, hi] y detectar cambios de signo entre
       puntos adyacentes; en cada cruce refinar con ``brentq``.
    2. Si no hay cruce, devolver el argumento que minimiza ``|func|`` cuando
       el mínimo es numéricamente cero (equilibrio en el borde del dominio).
    3. Si no hay raíz, lanzar :class:`ValueError` con diagnóstico útil.
    """
    lo, hi = float(lo), float(hi)
    if not (np.isfinite(lo) and np.isfinite(hi)):
        raise ValueError(
            "Intervalo no finito para solve_1d "
            f"(lo={lo!r}, hi={hi!r}). Revise la calibración."
        )
    if hi <= lo:
        raise ValueError(
            f"Intervalo inválido para solve_1d: lo={lo:g} no es menor que hi={hi:g}."
        )
    samples = np.linspace(lo, hi, n)
    values = np.asarray([func(x) for x in samples], dtype=float)
    for i in range(len(values) - 1):
        a, b = samples[i], samples[i + 1]
        fa, fb = values[i], values[i + 1]
        if not (np.isfinite(fa) and np.isfinite(fb)):
            continue
        if fa == 0.0:
            return float(a)
        if fa * fb < 0.0:
            return float(brentq(func, a, b, xtol=1e-12))
    finite = np.isfinite(values)
    if finite.any():
        abs_vals = np.abs(values[finite])
        idx = int(np.argmin(abs_vals))
        best_x = float(np.asarray(samples, dtype=float)[finite][idx])
        best_f = float(abs_vals[idx])
        # Refinar el mínimo muestreado con minimización acotada: captura
        # tangencias (función que toca el eje sin cruzarlo) en el borde.
        try:
            res = minimize_scalar(
                func, bounds=(lo, hi), method="bounded", options={"xatol": 1e-12}
            )
            if np.isfinite(res.fun) and abs(res.fun) < best_f:
                best_x, best_f = float(res.x), float(abs(res.fun))
        except (ValueError, RuntimeError):
            pass
        scale = 1.0 + max(float(np.nanmax(abs_vals)), 1.0)
        if best_f <= 1e-6 * scale:
            return best_x
        raise ValueError(
            "No se encontró raíz de la función en "
            f"[{lo:g}, {hi:g}] (|f| mínimo = {best_f:.3g}). "
            "Revise la calibración de parámetros o amplíe el dominio."
        )
    raise ValueError(f"La función no devuelve valores finitos en [{lo:g}, {hi:g}].")


def solve_system(funcs: Callable[[np.ndarray], np.ndarray], x0: np.ndarray) -> np.ndarray:
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
        sol, _info, ier, _ = fsolve(funcs, start, full_output=True, xtol=1e-10)
        if ier == 1 and np.all(np.isfinite(sol)):
            return np.asarray(sol, dtype=float)
    raise ValueError("No convergió el sistema de ecuaciones simultáneas.")


def feasible(f: float) -> bool:
    """Verifica que un valor sea finito y utilizable."""
    return bool(np.isfinite(f))
