"""Smoke tests de la aplicación Streamlit con AppTest."""

from __future__ import annotations

import pytest
from streamlit.testing.v1 import AppTest

from sicm_core.engine.registry import registry

APP = "research_lab/app.py"


@pytest.fixture
def app():
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    return at


def _assert_ok(at, label):
    if at.exception:
        raise AssertionError(f"{label}: {at.exception}")


def test_app_boots(app):
    _assert_ok(app, "arranque")
    assert "result" not in app.session_state


@pytest.mark.parametrize("model", registry.names())
def test_dashboard_runs_every_model(app, model):
    app.sidebar.selectbox[0].set_value(model)
    app.run()
    _assert_ok(app, f"{model}: selección")
    app.sidebar.button[0].click()
    app.run()
    _assert_ok(app, f"{model}: ejecutar")
    assert "result" in app.session_state
    assert "experiment" in app.session_state


def test_dashboard_export_pdf(app):
    app.sidebar.selectbox[0].set_value("islm")
    app.run()
    app.sidebar.button[0].click()
    app.run()
    _assert_ok(app, "ejecutar islm")
    app.button(key="export_pdf").click()
    app.run()
    _assert_ok(app, "exportar PDF")


def test_dashboard_export_xlsx(app):
    app.sidebar.selectbox[0].set_value("islm")
    app.run()
    app.sidebar.button[0].click()
    app.run()
    _assert_ok(app, "ejecutar islm")
    app.button(key="export_xlsx").click()
    app.run()
    _assert_ok(app, "exportar Excel")


def test_sensitivity_page_needs_experiment(app):
    app.sidebar.radio[0].set_value("🧪 Laboratorio de Sensibilidad")
    app.run()
    _assert_ok(app, "sensibilidad sin experimento")
    assert "sens_df" not in app.session_state


def test_experiments_store_page(app):
    app.sidebar.radio[0].set_value("💾 Experimentos")
    app.run()
    _assert_ok(app, "página experimentos")


def test_docs_page(app):
    app.sidebar.radio[0].set_value("📚 Documentación")
    app.run()
    _assert_ok(app, "página documentación")
