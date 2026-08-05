"""SICM Research Lab — aplicación Streamlit.

Nuevo flujo:
    Sidebar → Scenario → Experiment → Engine → Result → Dashboard
"""

from __future__ import annotations

import sys
from pathlib import Path

# Garantiza que el paquete sicm_core sea importable al ejecutar la app desde
# el directorio de la app (p. ej. Streamlit Cloud / GitHub Actions), donde
# sys.path[0] apunta a research_lab/ y no a la raíz del repositorio.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import streamlit as st

from research_lab.reports.pdf import generate_pdf_report
from research_lab.ui.controls import (
    build_scenario,
    expectations_selector,
    horizon_selector,
    parameter_editor,
    regime_selector,
    shock_selector,
)
from research_lab.visualization.plots import _LABELS, plot_result
from sicm_core import Engine, registry
from sicm_core.analysis.sensitivity import one_factor_at_a_time
from sicm_core.analysis.shocks import apply_shocks
from sicm_core.branding import (
    AUTHOR,
    EMAIL,
    GITHUB,
    VERSION,
    institution_line,
)
from sicm_core.engine.dispatcher import dispatch
from sicm_core.engine.errors import SimulationError
from sicm_core.experiments import default_scenario, new_experiment
from sicm_core.experiments.scenario import Scenario
from sicm_core.io import ExperimentStore, result_to_excel

st.set_page_config(
    page_title="SICM Research Lab",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

ASSETS_DIR = Path(__file__).parent / "assets"
LOGO_PATH = ASSETS_DIR / "escudo_unal_color.png"

LABELS = registry.labels()
STORE_DIR = Path(__file__).parent / "data" / "experiments"
PAGES = [
    "📊 Dashboard",
    "🧪 Laboratorio de Sensibilidad",
    "💾 Experimentos",
    "📚 Documentación",
]

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
        st.divider()
        page = st.radio("Navegación", PAGES, key="nav")
        st.divider()
        if PAGES_MAP[page] == "dashboard":
            model = st.selectbox(
                "Modelo",
                list(LABELS),
                key="model",
                format_func=lambda m: LABELS[m],
            )
            params = default_scenario(model).parameters
            st.session_state["params"] = parameter_editor(model, params)
            if model in ("mundell_fleming", "islm_bp", "integrated"):
                st.session_state["regime"] = regime_selector()
            if model in ("as_ad", "four_quadrant"):
                st.session_state["horizon_val"] = horizon_selector()
            if model == "new_classical":
                st.session_state["expectations_val"] = expectations_selector()
            st.session_state["shock"] = shock_selector(model)
            st.session_state["scenario"] = build_scenario(
                model,
                st.session_state["params"],
                st.session_state.get("shock"),
                st.session_state.get("regime"),
                st.session_state.get("horizon_val"),
                st.session_state.get("expectations_val"),
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
    try:
        result = _engine().run(experiment)
    except SimulationError as exc:
        st.session_state.pop("result", None)
        st.session_state.pop("experiment", None)
        st.error(f"⚠️ {exc}")
        return
    st.session_state["experiment"] = experiment
    st.session_state["result"] = result
    st.session_state["result_key"] = experiment.id


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------
def _metric_column(result, key, label, fmt):
    b = result.baseline.get(key)
    f = result.equilibrium.get(key)
    if f is None:
        return
    delta = f - b if b is not None else None
    if delta is None:
        st.metric(label, fmt(f))
        return
    st.metric(label, fmt(f), fmt(delta) if abs(delta) > 1e-12 else "sin cambio")


def _dashboard_metrics(result):
    eq = result.equilibrium
    cols = st.columns(4)
    with cols[0]:
        _metric_column(result, "Y", "Producto (Y)", lambda v: f"{v:,.1f}")
    with cols[1]:
        _metric_column(result, "r", "Tasa (r)", lambda v: f"{v * 100:.2f}%")
    with cols[2]:
        if eq.get("P") is not None:
            _metric_column(result, "P", "Precios (P)", lambda v: f"{v:.3f}")
        elif eq.get("u") is not None:
            _metric_column(result, "u", "Desempleo (u)", lambda v: f"{v * 100:.2f}%")
    with cols[3]:
        if eq.get("e") is not None:
            _metric_column(result, "e", "Tipo de cambio (e)", lambda v: f"{v:,.1f}")
        elif eq.get("pi") is not None:
            _metric_column(result, "pi", "Inflación (π)", lambda v: f"{v * 100:.2f}%")


def _executive_summary(result):
    """Banner con la lectura ejecutiva y las cuatro mayores variaciones."""
    direction = result.interpretation.direction
    emoji = {"expansivo": "🟢", "contractivo": "🔴", "neutro": "⚪"}[direction]
    top = sorted(
        (
            (key, info["delta"])
            for key, info in result.variable_table().items()
            if info["delta"] is not None
        ),
        key=lambda kv: abs(kv[1]),
        reverse=True,
    )[:4]
    chips = " &nbsp;·&nbsp; ".join(
        f"<b>{_LABELS.get(k, k)}</b> {v:+,.2f}" for k, v in top
    )
    st.markdown(
        f"""
        <div style="background:#eef3f8;border-left:4px solid #2f6fb3;
                    padding:0.8rem 1rem;border-radius:6px;margin-bottom:1rem;">
            <b>Resumen ejecutivo</b> {emoji} {result.interpretation.summary}
            <div style="margin-top:0.4rem;font-size:0.95rem;">{chips}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_dashboard():
    st.title("📊 Dashboard de Resultados")
    result = st.session_state.get("result")
    if result is None:
        st.info(
            "Configure el escenario en la barra lateral y pulse «Ejecutar experimento»."
        )
        return

    model = st.session_state["experiment"].scenario.model
    direction = result.interpretation.direction
    emoji = {"expansivo": "🟢", "contractivo": "🔴", "neutro": "⚪"}[direction]

    st.subheader(f"{LABELS[model]} · efecto {direction} {emoji}")
    _executive_summary(result)
    _dashboard_metrics(result)

    st.divider()
    scenario = st.session_state["experiment"].scenario
    base_model = dispatch(scenario)
    final_model = None
    if scenario.shocks:
        shocked_params, _ = apply_shocks(scenario.parameters, scenario.shocks)
        final_model = dispatch(
            Scenario(model=model, parameters=shocked_params, metadata=scenario.metadata)
        )

    col1, col2 = st.columns([3, 2])
    with col1:
        fig = plot_result(result, base_model, final_model)
        st.plotly_chart(fig, width="stretch")
    with col2:
        st.subheader("Interpretación")
        st.markdown(result.interpretation.summary)
        for bullet in result.interpretation.bullets:
            st.markdown(f"- {bullet}")
        st.subheader("Canales de transmisión")
        for channel in result.transmission.channels:
            st.markdown(f"- {channel}")

    if model == "four_quadrant":
        _dashboard_four_quadrant(result, final_model or base_model)

    with st.expander("🗂️ Leyenda de variables utilizadas"):
        for key in result.equilibrium:
            st.markdown(f"- **`{key}`** — {_LABELS.get(key, key)}")

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
                path = generate_pdf_report(
                    result, tmp.name, title="Reporte SICM Research Lab"
                )
                st.download_button(
                    "⬇️ PDF",
                    Path(path).read_bytes(),
                    "reporte_sicm.pdf",
                    "application/pdf",
                    key="dl_pdf",
                )
        if c2.button("📊 Descargar Excel", key="export_xlsx"):
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
                result_to_excel(result, tmp.name)
                st.download_button(
                    "⬇️ Excel",
                    Path(tmp.name).read_bytes(),
                    "resultado_sicm.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_xlsx",
                )
        if c3.button("🗂️ Guardar en el almacén", key="store_save"):
            _store().save(st.session_state["experiment"])
            st.success(f"Guardado: {st.session_state['experiment'].id}")

    _footer()


def _dashboard_four_quadrant(result, final_model):
    """Secciones específicas del modelo de cuatro cuadrantes."""
    from research_lab.visualization.plots import (
        plot_convergence,
        plot_transmission_mechanism,
    )
    from sicm_core.models.four_quadrant import transmission_steps

    scenario = st.session_state["experiment"].scenario

    st.divider()
    st.subheader("🧩 Mecanismo de transmisión entre cuadrantes")
    if scenario.shocks:
        target = scenario.shocks[0].target
        steps = transmission_steps(target, result.baseline, result.equilibrium)
        fig = plot_transmission_mechanism(steps, result.baseline, result.equilibrium)
        st.plotly_chart(fig, width="stretch")
        for paso in steps:
            origen = " · **origen del choque**" if paso["valor"] == "origen" else ""
            st.markdown(f"**{paso['titulo']}**{origen}\n\n{paso['detalle']}")
    else:
        st.info("Aplique un choque para visualizar el mecanismo de transmisión.")

    st.divider()
    st.subheader("⏳ Convergencia dinámica (expectativas adaptativas)")
    c1, c2 = st.columns([1, 2])
    with c1:
        speed = st.slider(
            "Velocidad de ajuste de P^e", 0.05, 0.9, 0.3, 0.05, key="fq_speed"
        )
        periods = st.slider("Horizonte (periodos)", 5, 40, 20, 5, key="fq_periods")
    with c2:
        fig = plot_convergence(final_model, periods=periods, speed=speed)
        st.plotly_chart(fig, width="stretch")

    with st.expander("📋 Tabla de los cuatro cuadrantes"):
        st.markdown(
            """
            | Cuadrante | Plano | Variables | Función |
            |---|---|---|---|
            | **II** (superior izquierdo) | IS-LM | (Y, i) | Equilibrio de bienes (IS) y dinero (LM) |
            | **III** (inferior izquierdo) | AD-AS | (Y, P) | DA derivada de IS-LM vs. OA de corto plazo |
            | **IV** (inferior derecho) | Demanda de trabajo | (N, W/P) | W/P = PMgL (productividad marginal) |
            | **I** (superior derecho) | Oferta de trabajo | (N, W) | W ajusta según N^s = N₀ + η·(W/P^e) |

            **Lazo de retroalimentación:** II → Y → III → P → IV → W/P → N → I → W → II.
            """
        )


def page_sensitivity():
    st.title("🧪 Laboratorio de Sensibilidad")
    st.caption(
        "Análisis unifactorial: varía un parámetro y mide el efecto en el equilibrio."
    )
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
        "as_ad": ["G", "M", "Yn", "lambda_pc"],
        "islm_bp": ["G", "M", "r_w", "kappa"],
        "new_keynesian": ["G", "pi_target", "sigma", "phi_taylor"],
        "new_classical": ["M", "Pe", "Yn", "alpha_lucas"],
        "okun": ["Y_obs", "Yn", "beta_okun"],
        "phillips": ["Y_obs", "pi_e", "lambda_pc"],
        "integrated": ["G", "M", "r_w", "Yn", "pi_target"],
        "four_quadrant": ["G", "M", "A_prod", "Pe", "lambda_pc"],
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
            go.Scatter(
                x=df[param].tolist(), y=df[ycol].tolist(), mode="lines+markers", name=ycol
            )
        )
        fig.update_layout(
            title=f"Sensibilidad de {ycol} a {param}",
            xaxis_title=param,
            yaxis_title=ycol,
            template="plotly_white",
        )
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
        ## Objetivos

        SICM Research Lab es una plataforma de **simulación y análisis de
        economía macroeconómica** diseñada para el estudio de los efectos de
        la política fiscal, monetaria, cambiaria y de expectativas sobre el
        equilibrio de la economía. Sus objetivos son:

        - **Modelar** los principales marcos teóricos de la macroeconomía en
          un mismo entorno: keynesiano (IS-LM, Mundell-Fleming, OA-DA,
          IS-LM-BP), neokeynesiano (3 ecuaciones), clásico (cerrado, abierto
          y nuevo/curva de Lucas), mercado laboral (Okun y Phillips), el
          macromodelo integrado de cuatro planos y el equilibrio general de
          cuatro cuadrantes (IS-LM, AD-AS y mercado laboral).
        - **Simular** escenarios de equilibrio base y con choques, con
          parámetros ajustables de forma interactiva.
        - **Analizar** los resultados mediante interpretación automática en
          lenguaje natural, canales de transmisión, comparaciones base vs.
          choque y análisis de sensibilidad unifactorial.
        - **Documentar y exportar** experimentos (PDF, Excel) para su uso
          académico y de investigación.
        """
    )

    st.markdown(
        """
        ## La plataforma

        El laboratorio se organiza en dos paquetes complementarios:

        - **`sicm_core`** — biblioteca reutilizable que contiene los modelos,
          el motor de ejecución, los análisis (choques, políticas,
          sensibilidad), los resultados (interpretación, transmisión) y las
          utilidades de entrada/salida.
        - **`research_lab`** — interfaz interactiva construida con Streamlit
          (paneles de configuración, dashboard de resultados, laboratorio de
          sensibilidad, almacén de experimentos, documentación) y la capa de
          visualización y reportes.

        El flujo de datos sigue la cadena
        **Sidebar → Scenario → Experiment → Engine → Result → Dashboard**:
        la barra lateral configura el escenario, el motor resuelve el
        equilibrio del modelo con los parámetros y choques indicados, y el
        dashboard presenta las cifras, gráficas, interpretación y canales de
        transmisión.
        """
    )

    st.markdown(
        """
        ## Formas de uso

        1. **Seleccione el modelo** en la barra lateral y ajuste los
           parámetros con los deslizadores del panel «Parámetros del modelo».
        2. **Configure el contexto** del modelo según corresponda: régimen
           cambiario (economías abiertas), horizonte de corto/largo plazo
           (OA-DA) o formación de expectativas (clásico nuevo).
        3. **Aplique un choque** del catálogo (por ejemplo, +10 % de gasto
           público o una expansión monetaria) o ejecute sin choques para
           obtener el equilibrio de referencia.
        4. **Ejecute el experimento** y revise el dashboard: métricas,
           gráficas de curvas (IS-LM, IS-LM-BP, OA-DA, Phillips, Okun o los
           cuatro planos), interpretación automática y canales de transmisión.
        5. **Profundice** con el Laboratorio de Sensibilidad, variando un
           parámetro en un rango y midiendo el efecto sobre las variables del
           equilibrio.
        6. **Guarde y exporte** el experimento en el almacén o descargue el
           reporte en PDF o Excel.
        """
    )

    st.markdown(
        """
        ## Formas de análisis

        - **Equilibrio base:** solución del modelo con la calibración de
          referencia, sin perturbaciones.
        - **Choques:** perturbaciones proporcionales o absolutas sobre un
          parámetro (gasto, impuestos, dinero, tasas, expectativas, ancla
          cambiaria, productividad), con comparación base vs. final.
        - **Políticas:** expansión/contracción fiscal y monetaria como
          choques predefinidos.
        - **Sensibilidad:** efecto de un parámetro sobre las variables del
          equilibrio a lo largo de un rango de valores.
        - **Interpretación:** lectura automática del resultado que describe
          la dirección del efecto (expansivo, contractivo o neutro) y las
          variables relevantes.
        - **Transmisión:** canales a través de los cuales se propaga el
          choque según la estructura de mercado del modelo.
        - **Exportación:** reporte PDF y hoja de cálculo Excel con la tabla
          de variables base, final y variación.
        """
    )

    st.subheader("Modelos registrados")
    st.table(pd.DataFrame(_engine().catalog()))
    st.subheader("Catálogo de choques")
    from sicm_core.analysis.shocks import SHOCK_CATALOG

    for model, shocks in SHOCK_CATALOG.items():
        st.write(f"**{LABELS.get(model, model)}**")
        for spec in shocks:
            st.write(
                f"- `{spec.target}` ± {spec.magnitude * 100:.0f}% · {spec.description}"
            )
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
