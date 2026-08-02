"""Visualización Plotly de resultados del motor SICM."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from sicm_core.results.equilibrium import Equilibrium, EquilibriumResult

_LABELS = {
    "Y": "Producto (Y)",
    "r": "Tasa de interés (r, %)",
    "P": "Nivel de precios (P)",
    "e": "Tipo de cambio (e)",
    "M": "Oferta monetaria (M)",
    "NX": "Exportaciones netas (NX)",
    "BP": "Balance de pagos (BP)",
    "C": "Consumo (C)",
    "I": "Inversión (I)",
    "S": "Ahorro (S)",
}


def _display_value(key: str, value: float | None) -> float | None:
    if value is None:
        return None
    return value * 100.0 if key == "r" else value


def _range_around(center: float, span: float = 0.35, lo: float = 1.0) -> np.ndarray:
    return np.linspace(max(center * (1 - span), lo), center * (1 + span), 200)


def plot_comparison(result: EquilibriumResult) -> go.Figure:
    """Barras agrupadas: base vs. final para las variables del equilibrio."""
    keys = [k for k in result.equilibrium.keys() if k not in ("CF",)]
    base_vals = [_display_value(k, result.baseline.get(k)) for k in keys]
    final_vals = [_display_value(k, result.equilibrium[k]) for k in keys]
    labels = [_LABELS.get(k, k) for k in keys]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(name="Base", x=labels, y=base_vals, marker_color="#5b9bd5")
    )
    fig.add_trace(
        go.Bar(name="Con choque", x=labels, y=final_vals, marker_color="#ed7d31")
    )
    fig.update_layout(
        barmode="group",
        title="Comparación de equilibrio (base vs. con choque)",
        yaxis_title="Valor",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def _equilibrium_marker(eq: Equilibrium, name: str, color: str) -> go.Scatter:
    y = _display_value("r", eq.get("r"))
    return go.Scatter(
        x=[eq["Y"]],
        y=[y] if y is not None else [eq["Y"]],
        mode="markers",
        name=name,
        marker=dict(symbol="star", size=14, color=color, line=dict(width=1, color="black")),
    )


def plot_is_lm(model, final_model=None) -> go.Figure:
    """Curvas IS/LM del modelo base y (opcional) del modelo con choque."""
    fig = go.Figure()
    y_eq = model.solve()["Y"]
    ys = _range_around(y_eq)
    traces = [("Base", model, "#1f77b4")]
    if final_model is not None:
        traces.append(("Choque", final_model, "#d62728"))
    for label, mdl, color in traces:
        y_vals, r_vals = mdl.is_curve(ys)
        fig.add_trace(
            go.Scatter(x=y_vals, y=r_vals * 100, name=f"IS · {label}",
                       line=dict(color=color, dash="dot"))
        )
        y_vals, r_vals = mdl.lm_curve(ys)
        fig.add_trace(
            go.Scatter(x=y_vals, y=r_vals * 100, name=f"LM · {label}",
                       line=dict(color=color, dash="dash"))
        )
        eq = mdl.solve()
        fig.add_trace(
            go.Scatter(x=[eq["Y"]], y=[eq["r"] * 100], mode="markers",
                       name=f"Equilibrio {label.lower()}",
                       marker=dict(symbol="star", size=16, color=color,
                                   line=dict(width=1, color="black")))
        )
    fig.update_layout(
        title="Modelo IS-LM: curvas IS y LM",
        xaxis_title="Producción (Y)",
        yaxis_title="Tasa de interés (r, %)",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def plot_mundell_fleming(model, final_model=None) -> go.Figure:
    """Curvas IS*/LM* en el plano (Y, e) y puntos de equilibrio."""
    fig = go.Figure()
    y_eq = model.solve()["Y"]
    ys = _range_around(y_eq)
    traces = [("Base", model, "#1f77b4")]
    if final_model is not None:
        traces.append(("Choque", final_model, "#d62728"))
    for label, mdl, color in traces:
        y_vals, e_vals = mdl.is_curve(ys)
        fig.add_trace(
            go.Scatter(x=y_vals, y=e_vals, name=f"IS* · {label}",
                       line=dict(color=color, dash="dot"))
        )
        y_vals, e_vals = mdl.lm_curve(ys)
        fig.add_trace(
            go.Scatter(x=y_vals, y=e_vals, name=f"LM* · {label}",
                       line=dict(color=color, dash="dash"))
        )
        eq = mdl.solve()
        fig.add_trace(
            go.Scatter(x=[eq["Y"]], y=[eq["e"]], mode="markers",
                       name=f"Equilibrio {label.lower()}",
                       marker=dict(symbol="star", size=16, color=color,
                                   line=dict(width=1, color="black")))
        )
    fig.update_layout(
        title="Modelo Mundell-Fleming: curvas IS* y LM*",
        xaxis_title="Producción (Y)",
        yaxis_title="Tipo de cambio nominal (e)",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def plot_result(result: EquilibriumResult, model, final_model=None) -> go.Figure:
    """Figura principal para un resultado (barras + curvas según modelo)."""
    if model.name == "islm":
        return plot_is_lm(model, final_model)
    if model.name == "mundell_fleming":
        return plot_mundell_fleming(model, final_model)
    return plot_comparison(result)
