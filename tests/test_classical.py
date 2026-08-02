"""Tests de los modelos clásicos (dicotomía y crowding-out)."""

import pytest

from sicm_core.engine import dispatch
from sicm_core.experiments import default_scenario
from sicm_core.experiments.scenario import Shock


def _solve(model, shock=None):
    scenario = default_scenario(model)
    if shock is None:
        return dispatch(scenario).solve()
    return dispatch(scenario).solve_with_shocks([shock])


def test_closed_baseline():
    eq = _solve("classical_closed")
    assert eq.Y == pytest.approx(1000.0)
    assert eq.P == pytest.approx(0.35, rel=1e-3)
    assert eq.r == pytest.approx(0.05, rel=1e-3)


def test_closed_money_neutral():
    baseline, final = _solve("classical_closed", Shock("M", 0.10))
    assert final.P == pytest.approx(baseline.P * 1.10, rel=1e-9)
    assert final.Y == pytest.approx(baseline.Y)
    assert final.r == pytest.approx(baseline.r)


def test_closed_fiscal_crowding_out():
    baseline, final = _solve("classical_closed", Shock("G", 0.10))
    assert final.Y == pytest.approx(baseline.Y)   # pleno empleo
    assert final.r > baseline.r                   # sube la tasa
    assert final.I < baseline.I                   # cae la inversión


def test_open_baseline():
    eq = _solve("classical_open")
    assert eq.Y == pytest.approx(1000.0)
    assert eq.r == pytest.approx(0.05)


def test_open_fiscal_crowding_via_nx():
    baseline, final = _solve("classical_open", Shock("G", 0.10))
    assert final.Y == pytest.approx(baseline.Y)
    assert final.NX < baseline.NX    # caen las exportaciones netas
    assert final.e > baseline.e      # se deprecia el tipo de cambio


def test_open_money_neutral():
    baseline, final = _solve("classical_open", Shock("M", 0.10))
    assert final.P == pytest.approx(baseline.P * 1.10, rel=1e-9)
    assert final.Y == pytest.approx(baseline.Y)
    assert final.e == pytest.approx(baseline.e)
