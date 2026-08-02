"""SICM Research Lab — aplicación Streamlit.

Nuevo flujo:
    Sidebar → Scenario → Experiment → Engine → Result → Dashboard
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from sicm_core import Engine, registry
from sicm_core.analysis.shocks import apply_shocks
from sicm_core.analysis.sensitivity import one_factor_at_a_time
from sicm_core.branding import (
    AUTHOR,
    CAMPUS,
    EMAIL,
    GITHUB,
    INSTITUTION,
    VERSION,
    institution_line,
)
from sicm_core.engine.dispatcher import dispatch
from sicm_core.experiments import default_scenario, new_experiment
from sicm_core.experiments.scenario import Scenario
from sicm_core.io import ExperimentStore, result_to_excel
from research_lab.reports.pdf import generate_pdf_report
from research_lab.ui.controls import (
    build_scenario,
    parameter_editor,
    regime_selector,
    shock_selector,
)
from research_lab.visualization.plots import plot_comparison, plot_result

st.set_page_config(page_title="SICM Research Lab", page_icon="📈",
                   layout="wide", initial_sidebar_state="expanded")

ASSETS_DIR = Path(__file__).parent / "assets"
LOGO_PATH = ASSETS_DIR / "escudo_unal_color.png"

LABELS = registry.labels()
STORE_DIR = Path(__file__).parent / "data" / "experiments"
PAGES = ["📊 Dashboard", "🧪 Laboratorio de Sensibilidad", "💾 Experimentos",
         "📚 Documentación"]

PAGES_MAP = {
    "📊 Dashboard": "dashboard",
    "🧪 Laboratorio de Sensibilidad": "sensitivity",
    "💾 Experimentos": "experiments",
    "📚 Documentación": "docs",
}


@st.cache_resource
def _engine() -> Engine:
    return Engine()


def _store() -> ExperimentStore:
    return ExperimentStore(STORE_DIR)


def _footer():
    st.markdown(
        f"""
        <div style="text-align:center; margin-top:3rem; padding-top:1rem;
                    border-top:1px solid #d9d9d9; color:#666;
                    font-size:0.85rem; line-height:1.6;">
            <b>{AUTHOR}</b> · {institution_line()}<br/>
            <a href="mailto:{EMAIL}">{EMAIL}</a> ·
            <a href="{GITHUB}">github.com/edinsonvo</a><br/>
            <b>SICM by {EMAIL} · v{VERSION}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def _logo_b64() -> str:
    import base64

    return base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")


# ---------------------------------------------------------------------------
# Sidebar: Scenario
# ---------------------------------------------------------------------------
def _sidebar():
    with st.sidebar:
        st.markdown(
            f"""
            <div style="text-align:center; padding:0.25rem 0 0.75rem 0;">
                <img src="data:image/png;base64,{_logo_b64()}"
                     alt="Escudo Universidad Nacional de Colombia"
                     style="width:84px;"/>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("## 📈 SICM Research Lab")
        st.caption(f"v{VERSION} · Milestone 1 — Infraestructura")
        st.caption(f"{AUTHOR} · {INSTITUTION} · {CAMPUS}")
        st.divider()
        page = st.radio("Navegación", PAGES, key="nav")
        st.divider()
        if PAGES_MAP[page] == "dashboard":
            model = st.selectbox(
                "Modelo", list(LABELS), key="model",
                format_func=lambda m: LABELS[m],
            )
            params = default_scenario(model).parameters
            st.session_state["params"] = parameter_editor(model, params)
            if model == "mundell_fleming":
                st.session_state["regime"] = regime_selector()
            st.session_state["shock"] = shock_selector(model)
            st.session_state["scenario"] = build_scenario(
                model,
                st.session_state["params"],
                st.session_state.get("shock"),
                st.session_state.get("regime"),
            )
            st.divider()
            if st.button("▶️ Ejecutar experimento", type="primary", key="run"):
                _run_experiment()
        else:
            st.caption("Use la pestaña Dashboard para configurar el escenario.")
    return page


def _run_experiment():
    scenario = st.session_state["scenario"]
    label = scenario.shocks[0].description if scenario.shocks else "equilibrio base"
    experiment = new_experiment(
        name=f"{scenario.model} · {label}",
        description=label,
        author="Research Lab",
        scenario=scenario,
    )
    result = _engine().run(experiment)
    st.session_state["experiment"] = experiment
    st.session_state["result"] = result
    st.session_state["result_key"] = experiment.id


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------
def _metric_column(result, key, label, fmt):
    b = result.baseline.get(key)
    f = result.equilibrium[key]
    delta = f - b if b is not None else None
    if delta is None:
        st.metric(label, fmt(f))
        return
    st.metric(label, fmt(f), fmt(delta) if abs(delta) > 1e-12 else "sin cambio")


def page_dashboard():
    st.title("📊 Dashboard de Resultados")
    result = st.session_state.get("result")
    if result is None:
        st.info("Configure el escenario en la barra lateral y pulse "
                "«Ejecutar experimento».")
        return

    model = st.session_state["experiment"].scenario.model
    direction = result.interpretation.direction
    emoji = {"expansivo": "🟢", "contractivo": "🔴", "neutro": "⚪"}[direction]

    st.subheader(f"{LABELS[model]} · efecto {direction} {emoji}")
    cols = st.columns(4)
    with cols[0]:
        _metric_column(result, "Y", "Producto (Y)", lambda v: f"{v:,.1f}")
    with cols[1]:
        _metric_column(result, "r", "Tasa (r)", lambda v: f"{v * 100:.2f}%")
    if result.equilibrium.get("P") is not None:
        with cols[2]:
            _metric_column(result, "P", "Precios (P)", lambda v: f"{v:.3f}")
    if result.equilibrium.get("e") is not None:
        with cols[3]:
            _metric_column(result, "e", "Tipo de cambio (e)", lambda v: f"{v:,.1f}")

    st.divider()
    scenario = st.session_state["experiment"].scenario
    final_model = None
    if scenario.shocks:
        shocked_params, _ = apply_shocks(scenario.parameters, scenario.shocks)
        final_model = dispatch(
            Scenario(model=model, parameters=shocked_params,
                     metadata=scenario.metadata)
        )

    col1, col2 = st.columns([3, 2])
    with col1:
        fig = plot_result(result, dispatch(scenario), final_model)
        st.plotly_chart(fig, width="stretch")
    with col2:
        st.subheader("Interpretación")
        st.markdown(result.interpretation.summary)
        for bullet in result.interpretation.bullets:
            st.markdown(f"- {bullet}")
        st.subheader("Canales de transmisión")
        for channel in result.transmission.channels:
            st.markdown(f"- {channel}")

    st.divider()
    with st.expander("🔢 Tabla de variables"):
        table = result.variable_table()
        df = pd.DataFrame(
            [
                {
                    "Variable": k,
                    "Base": f"{v['base']:.4f}" if v["base"] is not None else "—",
                    "Final": f"{v['final']:.4f}",
                    "Δ": f"{v['delta']:+.4f}" if v["delta"] is not None else "—",
                }
                for k, v in table.items()
            ]
        )
        st.dataframe(df, width="stretch", hide_index=True)

    with st.expander("💾 Exportar resultado"):
        c1, c2, c3 = st.columns(3)
        if c1.button("📄 Descargar PDF", key="export_pdf"):
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                path = generate_pdf_report(result, tmp.name,
                                           title="Reporte SICM Research Lab")
                st.download_button(
                    "⬇️ PDF", open(path, "rb").read(), "reporte_sicm.pdf",
                    "application/pdf", key="dl_pdf")
        if c2.button("📊 Descargar Excel", key="export_xlsx"):
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
                result_to_excel(result, tmp.name)
                st.download_button(
                    "⬇️ Excel", open(tmp.name, "rb").read(),
                    "resultado_sicm.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_xlsx")
        if c3.button("🗂️ Guardar en el almacén", key="store_save"):
            _store().save(st.session_state["experiment"])
            st.success(f"Guardado: {st.session_state['experiment'].id}")

    _footer()


def page_sensitivity():
    st.title("🧪 Laboratorio de Sensibilidad")
    st.caption("Análisis unifactorial: varía un parámetro y mide el efecto en el equilibrio.")
    if "experiment" not in st.session_state:
        st.info("Ejecute primero un experimento en el Dashboard.")
        return
    model = st.session_state["experiment"].scenario.model
    scenario = st.session_state["scenario"]

    relevant = {
        "islm": ["G", "M", "T", "I0", "c"],
        "mundell_fleming": ["G", "M", "r_w", "NX0"],
        "classical_closed": ["M", "G", "Yn", "V"],
        "classical_open": ["M", "G", "r_w", "Yn"],
    }.get(model, ["G", "M"])

    c1, c2 = st.columns([1, 1])
    with c1:
        param = st.selectbox("Parámetro", relevant, key="sens_param")
        base = getattr(scenario.parameters, param)
        lo = st.number_input("Mínimo", value=float(base * 0.8), key="sens_lo")
        hi = st.number_input("Máximo", value=float(base * 1.2), key="sens_hi")
    with c2:
        points = st.slider("Número de puntos", 3, 21, 7, key="sens_points")
        st.caption(f"Valor base de {param}: **{base:g}**")
        if st.button("▶️ Ejecutar análisis", type="primary", key="sens_run"):
            grid = [lo + (hi - lo) * i / (points - 1) for i in range(points)]
            st.session_state["sens_df"] = one_factor_at_a_time(
                scenario, param, grid, engine=_engine()
            )

    df = st.session_state.get("sens_df")
    if df is not None:
        st.subheader("Tabla de sensibilidad")
        st.dataframe(df, width="stretch", hide_index=True)
        st.subheader("Gráfica de sensibilidad")
        y_options = [c for c in df.columns if not c.startswith("Δ") and c != param]
        ycol = st.selectbox("Variable (eje Y)", y_options, key="sens_y")
        import plotly.graph_objects as go

        fig = go.Figure(
            go.Scatter(x=df[param].tolist(), y=df[ycol].tolist(),
                       mode="lines+markers", name=ycol)
        )
        fig.update_layout(title=f"Sensibilidad de {ycol} a {param}",
                          xaxis_title=param, yaxis_title=ycol,
                          template="plotly_white")
        st.plotly_chart(fig, width="stretch")

    _footer()


def page_experiments():
    st.title("💾 Almacén de Experimentos")
    store = _store()
    st.caption(f"Directorio: `{STORE_DIR}`")
    experiments = store.load_all()
    st.write(f"Experimentos guardados: **{len(experiments)}**")
    if not experiments:
        st.info("Aún no hay experimentos guardados.")
    else:
        for exp in sorted(experiments, key=lambda e: e.created_at, reverse=True):
            with st.expander(f"{exp.name} · {exp.created_at:%Y-%m-%d %H:%M}"):
                st.write(f"**ID:** `{exp.id}`")
                st.write(f"**Modelo:** {exp.scenario.model} · **Autor:** {exp.author}")
                st.write(f"**Descripción:** {exp.description or '—'}")
                st.write(f"**Estado:** {exp.status}")
                if exp.result is not None:
                    st.markdown(exp.result.interpretation.summary)
                if st.button("🗑️ Eliminar", key=f"del_{exp.id}"):
                    store.delete(exp.id)
                    st.rerun()
    _footer()


def page_docs():
    st.title("📚 Documentación")
    c_logo, c_text = st.columns([1, 4])
    with c_logo:
        st.image(str(LOGO_PATH), width=110)
    with c_text:
        st.markdown(f"### {institution_line()}")
        st.markdown(
            f"**Autor:** {AUTHOR} · **Correo:** [{EMAIL}](mailto:{EMAIL}) · "
            f"**GitHub:** [{GITHUB}]({GITHUB})"
        )
        st.caption(f"SICM v{VERSION} · Simulador Integral de Choques Macroeconómicos")
    st.divider()
    st.markdown(
        """
        ## Milestone 1: Infraestructura

        **Nuevo flujo:** Sidebar → Scenario → Experiment → Engine → Result → Dashboard

        ### Paquetes
        - `sicm_core` — biblioteca reutilizable (modelos, motor, análisis, resultados, I/O).
        - `research_lab` — interfaz Streamlit, visualización y reportes.
        """
    )
    st.subheader("Modelos registrados")
    st.table(pd.DataFrame(_engine().catalog()))
    st.subheader("Catálogo de choques")
    from sicm_core.analysis.shocks import SHOCK_CATALOG

    for model, shocks in SHOCK_CATALOG.items():
        st.write(f"**{LABELS.get(model, model)}**")
        for spec in shocks:
            st.write(f"- `{spec.target}` ± {spec.magnitude * 100:.0f}% · {spec.description}")
    _footer()


def main():
    page = _sidebar()
    PAGES_MAP_funcs = {
        "dashboard": page_dashboard,
        "sensitivity": page_sensitivity,
        "experiments": page_experiments,
        "docs": page_docs,
    }
    PAGES_MAP_funcs[PAGES_MAP[page]]()


if __name__ == "__main__":
    main()
