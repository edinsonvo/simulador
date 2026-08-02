"""Componentes de interfaz (Streamlit) para construir escenarios."""

from __future__ import annotations

import streamlit as st

from sicm_core.experiments.scenario import EconomyParameters, Scenario, Shock

PARAM_LABELS = {
    "C0": "Consumo autónomo",
    "c": "Propensión marginal a consumir",
    "I0": "Inversión autónoma",
    "b": "Sensibilidad de la inversión a r",
    "G": "Gasto del gobierno",
    "T": "Impuestos",
    "M": "Oferta monetaria",
    "k": "Sensibilidad de la demanda de dinero a Y",
    "h": "Sensibilidad de la demanda de dinero a r",
    "P": "Nivel de precios",
    "Yn": "Producto natural",
    "V": "Velocidad del dinero",
    "s": "Propensión al ahorro",
    "r_w": "Tasa mundial (r_w)",
    "theta": "Sensibilidad de NX al tipo de cambio",
    "e_bar": "Ancla cambiaria",
    "NX0": "Exportaciones netas autónomas",
}

_RANGES: dict[str, tuple[float, float]] = {
    "C0": (0, 300), "c": (0.1, 0.95), "I0": (0, 400), "b": (0.05, 1.0),
    "G": (0, 400), "T": (0, 400), "M": (50, 800), "k": (0.05, 1.5),
    "h": (100, 3000), "P": (0.5, 2.0), "Yn": (200, 2000), "V": (0.1, 3.0),
    "s": (0.05, 0.5), "r_w": (0.01, 0.15), "theta": (0.1, 2.0),
    "e_bar": (50, 400), "NX0": (-100, 100),
}

REGIMES = ["Flexible", "Fijo"]


def parameter_editor(model: str, params: EconomyParameters,
                     key_prefix: str | None = None) -> EconomyParameters:
    """Edita los parámetros relevantes del modelo con sliders."""
    prefix = key_prefix or f"param_{model}"
    with st.expander("⚙️ Parámetros del modelo", expanded=True):
        relevant = _relevant_params(model)
        updates: dict[str, float] = {}
        for key in relevant:
            label = PARAM_LABELS.get(key, key)
            lo, hi = _RANGES.get(key, (0.0, 100.0))
            lo, hi = float(lo), float(hi)
            step = (hi - lo) / 200.0
            value = st.slider(label, lo, hi, float(getattr(params, key)), step,
                              key=f"{prefix}_{key}")
            updates[key] = value
        return params.with_values(**updates)


def _relevant_params(model: str) -> list[str]:
    groups = {
        "islm": ["C0", "c", "I0", "b", "G", "T", "M", "k", "h", "P"],
        "mundell_fleming": ["C0", "c", "I0", "b", "G", "T", "M", "k", "h", "r_w", "NX0", "theta", "e_bar"],
        "classical_closed": ["Yn", "C0", "c", "I0", "b", "G", "T", "s", "M", "V"],
        "classical_open": ["Yn", "C0", "c", "I0", "b", "G", "T", "s", "M", "V", "r_w", "NX0", "theta"],
    }
    return groups.get(model, [])


def regime_selector(default: str = "Flexible") -> str:
    """Selector de régimen cambiario (solo relevante en Mundell-Fleming)."""
    return st.radio("Régimen cambiario", REGIMES,
                    index=REGIMES.index(default) if default in REGIMES else 0,
                    key="mf_regime")


def shock_selector(model: str) -> Shock | None:
    """Selecciona un choque del catálogo del modelo (o ninguno)."""
    from sicm_core.analysis.shocks import shocks_for

    options = shocks_for(model)
    labels = [s.description for s in options]
    chosen = st.selectbox("Choque", ["(sin choque)"] + labels,
                          key="shock_picker")
    if chosen == "(sin choque)":
        return None
    return next(s for s in options if s.description == chosen)


def build_scenario(model: str, params: EconomyParameters, shock: Shock | None,
                   regime: str | None = None) -> Scenario:
    """Ensambla un escenario a partir de la interfaz."""
    metadata = {}
    if model == "mundell_fleming":
        metadata["regime"] = regime or "Flexible"
    scenario = Scenario(model=model, parameters=params, metadata=metadata,
                        label=f"Escenario {model}")
    if shock is not None:
        scenario = scenario.with_shocks(shock)
    return scenario
