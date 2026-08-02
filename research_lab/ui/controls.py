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
    "kappa": "Movilidad de capitales (κ)",
    "m": "Propensión marginal a importar",
    "u_n": "Tasa natural de desempleo",
    "beta_okun": "Coeficiente de Okun (β)",
    "pi": "Inflación observada",
    "pi_e": "Inflación esperada (π_e)",
    "lambda_pc": "Sensibilidad de la Phillips al gap",
    "pi_target": "Meta de inflación",
    "sigma": "Sensibilidad del gap a r (σ)",
    "phi_taylor": "Regla de Taylor (φ)",
    "r_star": "Tasa natural (r*)",
    "alpha_lucas": "Curva de Lucas (α)",
    "Pe": "Expectativa de precios (P^e)",
    "P_prev": "Nivel de precios previo (P_prev)",
    "G_ref": "Gasto de referencia (G_ref)",
    "Y_obs": "Producto observado (Y_obs)",
    "A_prod": "Productividad (A)",
    "alpha_prod": "Elasticidad del producto al trabajo (α)",
    "Nn": "Empleo natural (N_n)",
    "N0_s": "Oferta de trabajo autónoma (N_0)",
    "eta_s": "Sensibilidad de la oferta de trabajo (η)",
}

_RANGES: dict[str, tuple[float, float]] = {
    "C0": (0, 300), "c": (0.1, 0.95), "I0": (0, 400), "b": (0.05, 1.0),
    "G": (0, 400), "T": (0, 400), "M": (50, 800), "k": (0.05, 1.5),
    "h": (100, 3000), "P": (0.5, 2.0), "Yn": (200, 2000), "V": (0.1, 3.0),
    "s": (0.05, 0.5), "r_w": (0.01, 0.15), "theta": (0.1, 2.0),
    "e_bar": (50, 400), "NX0": (-100, 100), "kappa": (0.0, 3.0),
    "m": (0.05, 0.6), "u_n": (0.02, 0.15), "beta_okun": (0.5, 3.5),
    "pi": (0.0, 0.15), "pi_e": (0.0, 0.15), "lambda_pc": (0.1, 1.5),
    "pi_target": (0.0, 0.10), "sigma": (0.1, 1.5), "phi_taylor": (0.5, 3.0),
    "r_star": (0.0, 0.15), "alpha_lucas": (0.0, 1.0), "Pe": (0.5, 2.0),
    "P_prev": (0.5, 2.0), "G_ref": (0, 400), "Y_obs": (200, 2000),
    "A_prod": (50, 150), "alpha_prod": (0.2, 0.9), "Nn": (80, 120),
    "N0_s": (40, 100), "eta_s": (1.0, 12.0),
}

REGIMES = ["Flexible", "Fijo"]
HORIZONS = ["Corto plazo", "Largo plazo"]
EXPECTATIONS = ["Sorpresa (P^e fija)", "Anticipadas (P^e = P)"]


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
        "as_ad": ["C0", "c", "I0", "b", "G", "T", "M", "k", "h", "Yn", "P_prev", "lambda_pc"],
        "islm_bp": ["C0", "c", "I0", "b", "G", "T", "M", "k", "h", "r_w", "kappa", "NX0", "theta", "m", "e_bar"],
        "new_keynesian": ["Yn", "C0", "c", "G", "T", "G_ref", "sigma", "phi_taylor", "lambda_pc", "pi_e", "pi_target", "r_star", "u_n", "beta_okun"],
        "new_classical": ["Yn", "M", "V", "Pe", "P_prev", "alpha_lucas", "u_n", "beta_okun"],
        "okun": ["Yn", "Y_obs", "u_n", "beta_okun"],
        "phillips": ["Yn", "Y_obs", "pi_e", "lambda_pc", "u_n", "beta_okun"],
        "integrated": ["C0", "c", "I0", "b", "G", "T", "M", "k", "h", "Yn", "r_w", "kappa", "NX0", "theta", "m", "e_bar", "P_prev", "lambda_pc", "pi_e", "u_n", "beta_okun"],
        "four_quadrant": ["C0", "c", "I0", "b", "G", "T", "M", "k", "h", "Pe", "P_prev", "lambda_pc", "A_prod", "alpha_prod", "Nn", "N0_s", "eta_s"],
    }
    return groups.get(model, [])


def regime_selector(default: str = "Flexible") -> str:
    """Selector de régimen cambiario (economías abiertas)."""
    return st.radio("Régimen cambiario", REGIMES,
                    index=REGIMES.index(default) if default in REGIMES else 0,
                    key="mf_regime")


def horizon_selector(default: str = "Corto plazo") -> str:
    """Selector de horizonte temporal (modelos OA-DA)."""
    return st.radio("Horizonte", HORIZONS,
                    index=HORIZONS.index(default) if default in HORIZONS else 0,
                    key="horizon")


def expectations_selector(default: str = "Sorpresa (P^e fija)") -> str:
    """Selector de formación de expectativas (clásico nuevo)."""
    return st.radio("Formación de expectativas", EXPECTATIONS,
                    index=EXPECTATIONS.index(default) if default in EXPECTATIONS else 0,
                    key="expectations")


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
                   regime: str | None = None,
                   horizon: str | None = None,
                   expectations: str | None = None) -> Scenario:
    """Ensambla un escenario a partir de la interfaz."""
    metadata = {}
    if model in ("mundell_fleming", "islm_bp", "integrated"):
        metadata["regime"] = regime or "Flexible"
    if model == "as_ad":
        metadata["horizon"] = "largo" if horizon == "Largo plazo" else "corto"
    if model == "four_quadrant":
        metadata["horizon"] = "largo" if horizon == "Largo plazo" else "corto"
    if model == "new_classical":
        metadata["expectativas"] = (
            "anticipadas" if expectations == "Anticipadas (P^e = P)" else "sorpresa"
        )
    scenario = Scenario(model=model, parameters=params, metadata=metadata,
                        label=f"Escenario {model}")
    if shock is not None:
        scenario = scenario.with_shocks(shock)
    return scenario
