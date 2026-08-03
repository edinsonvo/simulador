"""Cobertura de la interpretación automática por familia de modelos."""

from __future__ import annotations

import pytest

from sicm_core.analysis.shocks import SHOCK_CATALOG
from sicm_core.engine import Engine
from sicm_core.experiments import default_scenario
from sicm_core.experiments.scenario import Shock

ENGINE = Engine()


def _interpret(model: str, shock: Shock | None = None):
    scenario = default_scenario(model)
    if shock is not None:
        scenario = scenario.with_shocks(shock)
    return ENGINE.run_scenario(scenario).interpretation


def _first_shock(model: str) -> Shock:
    spec = SHOCK_CATALOG[model][0]
    return Shock(spec.target, spec.magnitude, spec.description)


@pytest.mark.parametrize(
    ("model", "frase"),
    [
        ("islm", "mercado de bienes"),
        ("classical_closed", "dicotomía clásica"),
        ("new_keynesian", "regla de Taylor"),
        ("okun", "brecha de producto"),
        ("integrated", "cuatro planos"),
        ("four_quadrant", "cuatro cuadrantes"),
    ],
)
def test_family_summary_markers(model, frase):
    interp = _interpret(model, _first_shock(model))
    assert frase in interp.summary


def test_reference_title_and_direction():
    interp = _interpret("islm")
    assert "equilibrio de referencia" in interp.title
    assert interp.direction == "neutro"


def test_expansive_direction():
    interp = _interpret("islm", _first_shock("islm"))
    assert interp.direction == "expansivo"
    assert "Producto (Y)" in interp.bullets[0]


def test_contractive_direction():
    spec = SHOCK_CATALOG["islm"][1]  # G -10%
    interp = _interpret("islm", Shock(spec.target, spec.magnitude, spec.description))
    assert interp.direction == "contractivo"


def test_absolute_shock_description():
    shock = Shock("G", 25, absolute=True, description="")
    interp = _interpret("islm", shock)
    assert "aumento de G en +25 unidades" in interp.title


def test_percentage_shock_description():
    interp = _interpret("islm", _first_shock("islm"))
    assert "aumento del gasto público (+10%)" in interp.title


def test_labor_bullets_include_unemployment():
    interp = _interpret("okun", _first_shock("okun"))
    assert any("Desempleo (u)" in b for b in interp.bullets)


def test_four_quadrant_labor_bullets():
    interp = _interpret("four_quadrant", _first_shock("four_quadrant"))
    labels = " ".join(interp.bullets)
    assert "Empleo (N)" in labels
    assert "Salario real" in labels
