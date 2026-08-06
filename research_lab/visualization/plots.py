"""Visualización Plotly de resultados del motor SICM."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from sicm_core.results.equilibrium import Equilibrium, EquilibriumResult

_LABELS = {
    "Y": "Producto (Y)",
    "r": "Tasa de interés (r, %)",
    "P": "Nivel de precios (P)",
    "e": "Tipo de cambio (e)",
    "M": "Oferta monetaria (M)",
    "NX": "Exportaciones netas (NX)",
    "BP": "Balance de pagos (BP)",
    "CF": "Flujo de capitales (CF)",
    "C": "Consumo (C)",
    "I": "Inversión (I)",
    "S": "Ahorro (S)",
    "gap": "Brecha de producto (gap, %)",
    "pi": "Inflación (π, %)",
    "u": "Desempleo (u, %)",
    "Yn": "Producto natural (Yn)",
}


def _display_value(key: str, value: float | None) -> float | None:
    if value is None:
        return None
    if key in ("r", "gap", "pi", "u"):
        return value * 100.0
    return value


def _range_around(center: float, span: float = 0.35, lo: float = 1.0) -> np.ndarray:
    return np.linspace(max(center * (1 - span), lo), center * (1 + span), 200)


def plot_comparison(result: EquilibriumResult) -> go.Figure:
    """Perfil de equilibrio base vs. con choque (líneas, no barras)."""
    keys = [k for k in result.equilibrium if k not in ("CF",)]
    base_vals = [_display_value(k, result.baseline.get(k)) for k in keys]
    final_vals = [_display_value(k, result.equilibrium[k]) for k in keys]
    labels = [_LABELS.get(k, k) for k in keys]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=base_vals,
            name="Base",
            mode="lines+markers",
            line={"color": "#5b9bd5", "width": 3},
            marker={"size": 8},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=final_vals,
            name="Con choque",
            mode="lines+markers",
            line={"color": "#ed7d31", "width": 3},
            marker={"size": 8},
        )
    )
    fig.update_layout(
        title="Perfil del equilibrio (base vs. con choque)",
        yaxis_title="Valor",
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
    )
    return fig


def _equilibrium_marker(eq: Equilibrium, name: str, color: str) -> go.Scatter:
    y = _display_value("r", eq.get("r"))
    return go.Scatter(
        x=[eq["Y"]],
        y=[y] if y is not None else [eq["Y"]],
        mode="markers",
        name=name,
        marker={
            "symbol": "star",
            "size": 14,
            "color": color,
            "line": {"width": 1, "color": "black"},
        },
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
            go.Scatter(
                x=y_vals,
                y=r_vals * 100,
                name=f"IS · {label}",
                line={"color": color, "dash": "dot"},
            )
        )
        y_vals, r_vals = mdl.lm_curve(ys)
        fig.add_trace(
            go.Scatter(
                x=y_vals,
                y=r_vals * 100,
                name=f"LM · {label}",
                line={"color": color, "dash": "dash"},
            )
        )
        eq = mdl.solve()
        fig.add_trace(
            go.Scatter(
                x=[eq["Y"]],
                y=[eq["r"] * 100],
                mode="markers",
                name=f"Equilibrio {label.lower()}",
                marker={
                    "symbol": "star",
                    "size": 16,
                    "color": color,
                    "line": {"width": 1, "color": "black"},
                },
            )
        )
    fig.update_layout(
        title="Modelo IS-LM: curvas IS y LM",
        xaxis_title="Producción (Y)",
        yaxis_title="Tasa de interés (r, %)",
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
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
            go.Scatter(
                x=y_vals,
                y=e_vals,
                name=f"IS* · {label}",
                line={"color": color, "dash": "dot"},
            )
        )
        y_vals, e_vals = mdl.lm_curve(ys)
        fig.add_trace(
            go.Scatter(
                x=y_vals,
                y=e_vals,
                name=f"LM* · {label}",
                line={"color": color, "dash": "dash"},
            )
        )
        eq = mdl.solve()
        fig.add_trace(
            go.Scatter(
                x=[eq["Y"]],
                y=[eq["e"]],
                mode="markers",
                name=f"Equilibrio {label.lower()}",
                marker={
                    "symbol": "star",
                    "size": 16,
                    "color": color,
                    "line": {"width": 1, "color": "black"},
                },
            )
        )
    fig.update_layout(
        title="Modelo Mundell-Fleming: curvas IS* y LM*",
        xaxis_title="Producción (Y)",
        yaxis_title="Tipo de cambio nominal (e)",
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
    )
    return fig


def plot_result(result: EquilibriumResult, model, final_model=None) -> go.Figure:
    """Figura principal para un resultado (barras + curvas según modelo)."""
    if model.name == "islm":
        return plot_is_lm(model, final_model)
    if model.name == "mundell_fleming":
        return plot_mundell_fleming(model, final_model)
    if model.name == "as_ad":
        return plot_as_ad(model, final_model)
    if model.name == "islm_bp":
        return plot_islm_bp(model, final_model)
    if model.name == "okun":
        return plot_okun(model, final_model)
    if model.name == "phillips":
        return plot_phillips(model, final_model)
    if model.name == "integrated":
        return plot_integrated(model, final_model)
    if model.name == "four_quadrant":
        return plot_four_quadrant(model, final_model)
    return plot_comparison(result)


def _curve_trace(x, y, name, color, dash):
    return go.Scatter(x=x, y=y, name=name, line={"color": color, "dash": dash})


def _equilibrium_star(x, y, name, color):
    return go.Scatter(
        x=[x],
        y=[y],
        mode="markers",
        name=name,
        marker={
            "symbol": "star",
            "size": 16,
            "color": color,
            "line": {"width": 1, "color": "black"},
        },
    )


def _model_pairs(model, final_model):
    pairs = [("Base", model, "#1f77b4")]
    if final_model is not None:
        pairs.append(("Choque", final_model, "#d62728"))
    return pairs


def plot_as_ad(model, final_model=None) -> go.Figure:
    """Plano (Y, P): curvas DA y OA del modelo OA-DA."""
    fig = go.Figure()
    y_eq = model.solve()["Y"]
    ys = _range_around(y_eq, span=0.5)
    for label, mdl, color in _model_pairs(model, final_model):
        y_vals, p_vals = mdl.ad_curve(ys)
        fig.add_trace(_curve_trace(y_vals, p_vals, f"DA · {label}", color, "dot"))
        y_vals, p_vals = mdl.as_curve(ys)
        fig.add_trace(_curve_trace(y_vals, p_vals, f"OA · {label}", color, "dash"))
        eq = mdl.solve()
        fig.add_trace(
            _equilibrium_star(eq["Y"], eq["P"], f"Equilibrio {label.lower()}", color)
        )
    fig.update_layout(
        title="Modelo OA-DA: demanda y oferta agregadas",
        xaxis_title="Producción (Y)",
        yaxis_title="Nivel de precios (P)",
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
    )
    return fig


def plot_islm_bp(model, final_model=None) -> go.Figure:
    """Plano (Y, r): curvas IS, LM y BP del modelo IS-LM-BP."""
    fig = go.Figure()
    y_eq = model.solve()["Y"]
    ys = _range_around(y_eq, span=0.4)
    for label, mdl, color in _model_pairs(model, final_model):
        y_vals, r_vals = mdl.is_curve(ys)
        fig.add_trace(_curve_trace(y_vals, r_vals * 100, f"IS · {label}", color, "dot"))
        y_vals, r_vals = mdl.lm_curve(ys)
        fig.add_trace(_curve_trace(y_vals, r_vals * 100, f"LM · {label}", color, "dash"))
        y_vals, r_vals = mdl.bp_curve(ys)
        fig.add_trace(
            _curve_trace(y_vals, r_vals * 100, f"BP · {label}", color, "dashdot")
        )
        eq = mdl.solve()
        fig.add_trace(
            _equilibrium_star(
                eq["Y"], eq["r"] * 100, f"Equilibrio {label.lower()}", color
            )
        )
    fig.update_layout(
        title="Modelo IS-LM-BP: bienes, dinero y balanza de pagos",
        xaxis_title="Producción (Y)",
        yaxis_title="Tasa de interés (r, %)",
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
    )
    return fig


def plot_okun(model, final_model=None) -> go.Figure:
    """Plano (gap, u): la ley de Okun con su punto de equilibrio."""
    fig = go.Figure()
    gaps = np.linspace(-0.08, 0.08, 200)
    for label, mdl, color in _model_pairs(model, final_model):
        g, u = mdl.okun_curve(gaps)
        fig.add_trace(_curve_trace(g * 100, u * 100, f"Okun · {label}", color, "solid"))
    for label, mdl, color in _model_pairs(model, final_model):
        e = mdl.solve()
        fig.add_trace(
            _equilibrium_star(
                e["gap"] * 100, e["u"] * 100, f"Equilibrio {label.lower()}", color
            )
        )
    fig.update_layout(
        title="Ley de Okun: brecha de producto y desempleo",
        xaxis_title="Brecha de producto (gap, %)",
        yaxis_title="Desempleo (u, %)",
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
    )
    return fig


def plot_phillips(model, final_model=None) -> go.Figure:
    """Plano (gap, π): la curva de Phillips con su punto de equilibrio."""
    fig = go.Figure()
    gaps = np.linspace(-0.08, 0.08, 200)
    for label, mdl, color in _model_pairs(model, final_model):
        g, pi = mdl.phillips_curve(gaps)
        fig.add_trace(
            _curve_trace(g * 100, pi * 100, f"Phillips · {label}", color, "solid")
        )
    for label, mdl, color in _model_pairs(model, final_model):
        e = mdl.solve()
        fig.add_trace(
            _equilibrium_star(
                e["gap"] * 100, e["pi"] * 100, f"Equilibrio {label.lower()}", color
            )
        )
    fig.update_layout(
        title="Curva de Phillips: brecha de producto e inflación",
        xaxis_title="Brecha de producto (gap, %)",
        yaxis_title="Inflación (π, %)",
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
    )
    return fig


def plot_integrated(model, final_model=None) -> go.Figure:
    """Macro 4 planos: IS-LM, DA-OA, Phillips y Okun simultáneos."""
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "IS-LM (Y, r)",
            "DA-OA (Y, P)",
            "Curva de Phillips (gap, π)",
            "Ley de Okun (gap, u)",
        ),
    )
    y_eq = model.solve()["Y"]
    ys = _range_around(y_eq, span=0.4)
    gaps = np.linspace(-0.08, 0.08, 200)

    for label, mdl, color in _model_pairs(model, final_model):
        eq = mdl.solve()
        y, r = mdl.is_curve(ys)
        fig.add_trace(
            _curve_trace(y, r * 100, f"IS · {label}", color, "dot"), row=1, col=1
        )
        y, r = mdl.lm_curve(ys, price=eq["P"])
        fig.add_trace(
            _curve_trace(y, r * 100, f"LM · {label}", color, "dash"), row=1, col=1
        )
        y, p = mdl.ad_curve(ys)
        fig.add_trace(_curve_trace(y, p, f"DA · {label}", color, "dot"), row=1, col=2)
        y, p = mdl.as_curve(ys, price=eq["P"])
        fig.add_trace(_curve_trace(y, p, f"OA · {label}", color, "dash"), row=1, col=2)
        g, pi = mdl.phillips_curve(gaps)
        fig.add_trace(
            _curve_trace(g * 100, pi * 100, f"Phillips · {label}", color, "solid"),
            row=2,
            col=1,
        )
        g, u = mdl.okun_curve(gaps)
        fig.add_trace(
            _curve_trace(g * 100, u * 100, f"Okun · {label}", color, "solid"),
            row=2,
            col=2,
        )
        fig.add_trace(
            _equilibrium_star(eq["Y"], eq["r"] * 100, f"Eq · {label.lower()}", color),
            row=1,
            col=1,
        )
        fig.add_trace(
            _equilibrium_star(eq["Y"], eq["P"], f"Eq · {label.lower()}", color),
            row=1,
            col=2,
        )
        fig.add_trace(
            _equilibrium_star(
                eq["gap"] * 100, eq["pi"] * 100, f"Eq · {label.lower()}", color
            ),
            row=2,
            col=1,
        )
        fig.add_trace(
            _equilibrium_star(
                eq["gap"] * 100, eq["u"] * 100, f"Eq · {label.lower()}", color
            ),
            row=2,
            col=2,
        )
    fig.update_layout(
        title="Macromodelo integrado: los cuatro planos del análisis",
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
    )
    fig.update_xaxes(title_text="Producción (Y)", row=1, col=1)
    fig.update_yaxes(title_text="Tasa (r, %)", row=1, col=1)
    fig.update_xaxes(title_text="Producción (Y)", row=1, col=2)
    fig.update_yaxes(title_text="Precios (P)", row=1, col=2)
    fig.update_xaxes(title_text="Gap (%)", row=2, col=1)
    fig.update_yaxes(title_text="Inflación (π, %)", row=2, col=1)
    fig.update_xaxes(title_text="Gap (%)", row=2, col=2)
    fig.update_yaxes(title_text="Desempleo (u, %)", row=2, col=2)
    return fig


def _labor_zoom_range(models) -> tuple[tuple, tuple, tuple]:
    """Rangos de ejes centrados en el cruce de equilibrio de los planos
    laborales, de modo que el efecto del choque sea visible a pesar de que
    los desplazamientos de salarios y empleo son pequeños."""
    eqs = [m.solve() for m in models]
    ns = [eq["N"] for eq in eqs]
    nlo, nhi = min(ns), max(ns)
    span = max(nhi - nlo, 1.5)
    pad = 0.45 * span
    nlo, nhi = nlo - pad, nhi + pad
    nn = np.linspace(nlo, nhi, 120)
    nominal: list[np.ndarray] = []
    real: list[np.ndarray] = []
    for mdl, eq in zip(models, eqs):
        p = eq["P"]
        for _, w in (
            mdl.labor_supply_curve(nn),
            mdl.labor_demand_curve_nominal(nn, price=p),
        ):
            nominal.append(w[np.isfinite(w) & (w >= 0)])
        for _, w in (
            mdl.labor_supply_curve_real(nn, price=p),
            mdl.labor_demand_curve(nn),
        ):
            real.append(w[np.isfinite(w) & (w >= 0)])

    def _span(arrays: list[np.ndarray], floor: float) -> tuple[float, float]:
        vals = np.concatenate(arrays)
        if vals.size == 0:
            return (0.0, 1.0)
        lo, hi = float(vals.min()), float(vals.max())
        hspan = max(hi - lo, floor)
        hpad = 0.05 * hspan
        return (lo - hpad, hi + hpad)

    return (nlo, nhi), _span(nominal, 1e-3), _span(real, 1e-3)


def plot_four_quadrant(model, final_model=None) -> go.Figure:
    """Los cuatro cuadrantes interconectados: IS-LM, oferta de trabajo,
    AD-AS y demanda de trabajo."""
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Cuadrante II · IS-LM (Y, i)",
            "Cuadrante I · Mercado laboral (N, W)",
            "Cuadrante III · AD-AS (Y, P)",
            "Cuadrante IV · Mercado laboral (N, W/P)",
        ),
    )
    y_eq = model.solve()["Y"]
    ys = _range_around(y_eq, span=0.4)
    nn = model.parameters.Nn
    ns = np.linspace(0.75 * nn, 1.6 * nn, 200)

    for label, mdl, color in _model_pairs(model, final_model):
        e = mdl.solve()
        y, r = mdl.is_curve(ys)
        fig.add_trace(
            _curve_trace(y, r * 100, f"IS · {label}", color, "dot"), row=1, col=1
        )
        y, r = mdl.lm_curve(ys, price=e["P"])
        fig.add_trace(
            _curve_trace(y, r * 100, f"LM · {label}", color, "dash"), row=1, col=1
        )
        fig.add_trace(
            _equilibrium_star(e["Y"], e["r"] * 100, f"Eq · {label.lower()}", color),
            row=1,
            col=1,
        )

        n, w = mdl.labor_supply_curve(ns)
        mask = w >= 0
        fig.add_trace(
            _curve_trace(n[mask], w[mask], f"N^s · {label}", color, "dash"), row=1, col=2
        )
        n, w = mdl.labor_demand_curve_nominal(ns, price=e["P"])
        fig.add_trace(
            _curve_trace(n, w, f"N^d (W) · {label}", color, "dot"), row=1, col=2
        )
        fig.add_trace(
            _equilibrium_star(e["N"], e["W"], f"Eq · {label.lower()}", color),
            row=1,
            col=2,
        )

        y, p = mdl.ad_curve(ys)
        fig.add_trace(_curve_trace(y, p, f"DA · {label}", color, "dot"), row=2, col=1)
        y, p = mdl.as_curve(ys)
        fig.add_trace(_curve_trace(y, p, f"OA · {label}", color, "dash"), row=2, col=1)
        fig.add_trace(
            _equilibrium_star(e["Y"], e["P"], f"Eq · {label.lower()}", color),
            row=2,
            col=1,
        )

        n, w = mdl.labor_demand_curve(ns)
        fig.add_trace(_curve_trace(n, w, f"N^d · {label}", color, "solid"), row=2, col=2)
        n, w = mdl.labor_supply_curve_real(ns, price=e["P"])
        mask = w >= 0
        fig.add_trace(
            _curve_trace(n[mask], w[mask], f"N^s (W/P) · {label}", color, "dash"),
            row=2,
            col=2,
        )
        fig.add_trace(
            _equilibrium_star(e["N"], e["w"], f"Eq · {label.lower()}", color),
            row=2,
            col=2,
        )

    fig.update_layout(
        title="Equilibrio general en cuatro cuadrantes interconectados",
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
    )
    fig.update_xaxes(title_text="Producción (Y)", row=1, col=1)
    fig.update_yaxes(title_text="Tasa (i, %)", row=1, col=1)
    fig.update_xaxes(title_text="Producción (Y)", row=2, col=1)
    fig.update_yaxes(title_text="Precios (P)", row=2, col=1)
    (nlo, nhi), (wnom_lo, wnom_hi), (wreal_lo, wreal_hi) = _labor_zoom_range(
        [model] + ([final_model] if final_model is not None else [])
    )
    fig.update_xaxes(title_text="Empleo (N)", row=1, col=2, range=(nlo, nhi))
    fig.update_yaxes(
        title_text="Salario nominal (W)", row=1, col=2, range=(wnom_lo, wnom_hi)
    )
    fig.update_xaxes(title_text="Empleo (N)", row=2, col=2, range=(nlo, nhi))
    fig.update_yaxes(
        title_text="Salario real (W/P)", row=2, col=2, range=(wreal_lo, wreal_hi)
    )
    return fig


def plot_transmission_mechanism(steps, baseline, final) -> go.Figure:
    """Cadena de transmisión del choque entre los cuatro cuadrantes."""
    colors = {"II": "#1f77b4", "III": "#2ca02c", "IV": "#d62728", "I": "#9467bd"}
    xs = {"II": 0.14, "III": 0.39, "IV": 0.64, "I": 0.88}
    fig = go.Figure()
    for s in steps:
        c = s["cuadrante"]
        origin = s.get("valor") == "origen"
        fig.add_shape(
            type="rect",
            x0=xs[c] - 0.12,
            x1=xs[c] + 0.12,
            y0=0.35,
            y1=0.75,
            line={"color": colors[c], "width": 3},
            fillcolor=colors[c] if origin else "rgba(255,255,255,0.9)",
            opacity=0.9 if origin else 1.0,
        )
        fig.add_annotation(
            x=xs[c],
            y=0.66,
            text=s["titulo"],
            showarrow=False,
            font={"size": 12, "color": colors[c]},
            xref="paper",
            yref="paper",
        )
        fig.add_annotation(
            x=xs[c],
            y=0.46,
            text=s["detalle"],
            showarrow=False,
            font={"size": 10, "color": "black"},
            xref="paper",
            yref="paper",
        )
    arrows = [("II", "III"), ("III", "IV"), ("IV", "I")]
    for a, b in arrows:
        fig.add_annotation(
            x=xs[b] - 0.12,
            y=0.55,
            ax=xs[a] + 0.12,
            ay=0.55,
            xref="x domain",
            yref="y domain",
            axref="x domain",
            ayref="y domain",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.4,
            arrowcolor="#666666",
            arrowwidth=2.5,
        )
    fig.add_annotation(
        x=0.20,
        y=0.28,
        ax=0.82,
        ay=0.28,
        xref="x domain",
        yref="y domain",
        axref="x domain",
        ayref="y domain",
        text="retroalimentación: W → IS-LM",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.2,
        arrowcolor="#666666",
        arrowwidth=2,
        font={"size": 10},
    )
    fig.update_layout(
        title="Mecanismo de transmisión del choque entre cuadrantes",
        template="plotly_white",
        showlegend=False,
        xaxis={"visible": False, "range": [0, 1]},
        yaxis={"visible": False, "range": [0, 1]},
        height=300,
        margin={"t": 60, "b": 30},
    )
    return fig


def plot_convergence(model, periods: int = 20, speed: float = 0.3) -> go.Figure:
    """Ajuste dinámico con expectativas adaptativas hacia el largo plazo."""
    path = model.dynamic_simulation(periods=periods, speed=speed)
    t = list(range(len(path)))
    y = [e["Y"] for e in path]
    p = [e["P"] for e in path]
    pe = [e["Pe"] for e in path]
    u = [e["u"] * 100 for e in path]
    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=(
            "Producto (Y) → Yn",
            "Precios (P) y expectativas (P^e)",
            "Desempleo (u, %)",
        ),
    )
    color = "#1f77b4"
    fig.add_trace(
        go.Scatter(x=t, y=y, name="Y", line={"color": color, "width": 3}), row=1, col=1
    )
    fig.add_hline(y=path[-1]["Yn"], line_dash="dash", line_color="#999999", row=1, col=1)
    fig.add_trace(
        go.Scatter(x=t, y=p, name="P", line={"color": "#2ca02c", "width": 3}),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(x=t, y=pe, name="P^e", line={"color": "#d62728", "dash": "dash"}),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(x=t, y=u, name="u", line={"color": "#9467bd", "width": 3}),
        row=1,
        col=3,
    )
    fig.add_hline(y=0.0, line_dash="dash", line_color="#999999", row=1, col=3)
    fig.update_layout(
        title="Ajuste dinámico: convergencia al equilibrio de largo plazo",
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
    )
    fig.update_xaxes(title_text="Periodo (t)")
    return fig
