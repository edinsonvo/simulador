"""Exportación: PDF, Excel y serialización JSON de cada tipo de objeto."""

from __future__ import annotations

from uuid import UUID

import pandas as pd
import pytest

from research_lab.reports.pdf import generate_pdf_report
from sicm_core.analysis.shocks import shocks_for
from sicm_core.engine import Engine
from sicm_core.experiments import default_scenario, new_experiment
from sicm_core.experiments.scenario import Shock
from sicm_core.io import result_to_excel, save_json
from sicm_core.io.json_io import (
    equilibrium_from_dict,
    equilibrium_to_dict,
    load_json,
    result_from_dict,
    result_to_dict,
)
from sicm_core.results.equilibrium import Equilibrium

ENGINE = Engine()


def _completed(model: str = "islm"):
    scenario = default_scenario(model).with_shocks(shocks_for(model)[0])
    experiment = new_experiment(
        name="G+10%", description="qa", author="tester", scenario=scenario
    )
    ENGINE.run(experiment)
    return experiment


def test_pdf_report_generated(tmp_path):
    result = _completed().result
    path = generate_pdf_report(result, tmp_path / "reporte.pdf")
    assert path.exists()
    assert path.stat().st_size > 500
    assert path.read_bytes().startswith(b"%PDF")


def test_excel_read_back(tmp_path):
    result = _completed().result
    path = result_to_excel(result, tmp_path / "out.xlsx")
    sheets = pd.read_excel(path, sheet_name=None)
    assert sheets
    some = next(iter(sheets.values()))
    assert not some.empty


def test_json_scenario_roundtrip(tmp_path):
    scenario = default_scenario("four_quadrant").with_shocks(Shock("A_prod", +0.10))
    path = tmp_path / "sc.json"
    save_json(scenario, path)

    restored = load_json(path)
    assert restored.model == scenario.model
    assert restored.parameters.A_prod == scenario.parameters.A_prod
    assert restored.shocks[0].target == "A_prod"


def test_json_equilibrium_roundtrip():
    eq = Equilibrium(model="islm", variables={"Y": 1000.0, "r": 0.05})
    restored = equilibrium_from_dict(equilibrium_to_dict(eq))
    assert restored.model == eq.model
    assert restored["Y"] == pytest.approx(1000.0)


def test_json_result_roundtrip():
    result = _completed().result
    restored = result_from_dict(result_to_dict(result))
    assert restored.equilibrium["Y"] == result.equilibrium["Y"]
    assert restored.interpretation.title == result.interpretation.title
    assert restored.transmission.channels == result.transmission.channels


def test_json_result_without_baseline():
    result = _completed().result
    result.baseline = None
    restored = result_from_dict(result_to_dict(result))
    assert restored.baseline is None


def test_json_experiment_uuid(tmp_path):
    exp = _completed()
    path = tmp_path / "exp.json"
    save_json(exp, path)

    restored = load_json(path)
    assert isinstance(restored.id, UUID)
    assert restored.result is not None


def test_json_unserializable_raises(tmp_path):
    with pytest.raises(TypeError):
        save_json({"obj": object()}, tmp_path / "bad.json")
