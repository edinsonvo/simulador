"""Serialización JSON de objetos de sicm_core."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from ..experiments.experiment import Experiment
from ..experiments.scenario import EconomyParameters, Scenario, Shock
from ..results.equilibrium import Equilibrium, EquilibriumResult

_OBJECTS = {
    "EconomyParameters": EconomyParameters,
    "Shock": Shock,
    "Scenario": Scenario,
    "Equilibrium": Equilibrium,
    "EquilibriumResult": EquilibriumResult,
    "Experiment": Experiment,
}

_TAG = "__sicm_type__"


# -- Codificación -----------------------------------------------------------
def _default(obj: Any) -> Any:
    if isinstance(obj, UUID):
        return {"__uuid__": str(obj)}
    if isinstance(obj, datetime):
        return {"__datetime__": obj.isoformat()}
    raise TypeError(f"Objeto no serializable: {type(obj).__name__}")


def scenario_to_dict(scenario: Scenario) -> dict:
    return {
        _TAG: "Scenario",
        "model": scenario.model,
        "label": scenario.label,
        "parameters": economy_parameters_to_dict(scenario.parameters),
        "shocks": [shock_to_dict(s) for s in scenario.shocks],
        "metadata": dict(scenario.metadata),
    }


def economy_parameters_to_dict(params: EconomyParameters) -> dict:
    return {_TAG: "EconomyParameters", "values": params.as_dict()}


def shock_to_dict(shock: Shock) -> dict:
    return {
        _TAG: "Shock",
        "target": shock.target,
        "magnitude": shock.magnitude,
        "absolute": shock.absolute,
        "description": shock.description,
    }


def equilibrium_to_dict(eq: Equilibrium) -> dict:
    return {
        _TAG: "Equilibrium",
        "model": eq.model,
        "variables": eq.as_dict(),
        "label": eq.label,
    }


def result_to_dict(result: EquilibriumResult) -> dict:
    return {
        _TAG: "EquilibriumResult",
        "equilibrium": equilibrium_to_dict(result.equilibrium),
        "baseline": (
            equilibrium_to_dict(result.baseline) if result.baseline is not None else None
        ),
        "shocks": [shock_to_dict(s) for s in result.shocks],
        "plots": list(result.plots),
        "metrics": result.metrics.as_dict(),
        "interpretation": {
            "title": result.interpretation.title,
            "summary": result.interpretation.summary,
            "bullets": list(result.interpretation.bullets),
            "direction": result.interpretation.direction,
        },
        "transmission": {
            "channels": list(result.transmission.channels),
            "description": result.transmission.description,
        },
    }


def experiment_to_dict(experiment: Experiment) -> dict:
    return {
        _TAG: "Experiment",
        "id": str(experiment.id),
        "name": experiment.name,
        "description": experiment.description,
        "author": experiment.author,
        "created_at": experiment.created_at.isoformat(),
        "notes": experiment.notes,
        "status": experiment.status,
        "scenario": scenario_to_dict(experiment.scenario),
        "result": result_to_dict(experiment.result) if experiment.result else None,
    }


# -- Decodificación ---------------------------------------------------------
def scenario_from_dict(data: dict) -> Scenario:
    params = economy_parameters_from_dict(data["parameters"])
    shocks = [shock_from_dict(s) for s in data.get("shocks", [])]
    return Scenario(
        model=data["model"],
        label=data.get("label", ""),
        parameters=params,
        shocks=shocks,
        metadata=dict(data.get("metadata", {})),
    )


def economy_parameters_from_dict(data: dict) -> EconomyParameters:
    return EconomyParameters.from_mapping(data.get("values", {}))


def shock_from_dict(data: dict) -> Shock:
    return Shock(
        target=data["target"],
        magnitude=data["magnitude"],
        absolute=bool(data.get("absolute", False)),
        description=data.get("description", ""),
    )


def equilibrium_from_dict(data: dict) -> Equilibrium:
    return Equilibrium(
        model=data.get("model", ""),
        variables=data.get("variables", {}),
        label=data.get("label", "equilibrio"),
    )


def _rebuild_metrics(data: dict):
    from ..results.metrics import Metrics

    return Metrics(
        deltas=dict(data.get("deltas", {})),
        relative_changes=dict(data.get("relative_changes", {})),
        multipliers=dict(data.get("multipliers", {})),
    )


def _rebuild_interpretation(data: dict):
    from ..results.interpretation import Interpretation

    return Interpretation(
        title=data.get("title", ""),
        summary=data.get("summary", ""),
        bullets=list(data.get("bullets", [])),
        direction=data.get("direction", "neutro"),
    )


def _rebuild_transmission(data: dict):
    from ..results.transmission import Transmission

    return Transmission(
        channels=list(data.get("channels", [])),
        description=data.get("description", ""),
    )


def result_from_dict(data: dict) -> EquilibriumResult:
    result = EquilibriumResult(
        equilibrium=equilibrium_from_dict(data["equilibrium"]),
        baseline=(
            equilibrium_from_dict(data["baseline"]) if data.get("baseline") else None
        ),
        shocks=[shock_from_dict(s) for s in data.get("shocks", [])],
        plots=list(data.get("plots", [])),
        metrics=_rebuild_metrics(data.get("metrics", {})),
        interpretation=_rebuild_interpretation(data.get("interpretation", {})),
        transmission=_rebuild_transmission(data.get("transmission", {})),
    )
    return result


def experiment_from_dict(data: dict) -> Experiment:
    experiment = Experiment(
        id=UUID(data["id"]),
        name=data["name"],
        description=data.get("description", ""),
        author=data.get("author", "SICM Core"),
        created_at=datetime.fromisoformat(data["created_at"]),
        notes=data.get("notes", ""),
        status=data.get("status", "pending"),
        scenario=scenario_from_dict(data["scenario"]),
        result=result_from_dict(data["result"]) if data.get("result") else None,
    )
    return experiment


def _decode(obj: Any) -> Any:
    if isinstance(obj, dict):
        tag = obj.get(_TAG)
        if tag == "Experiment":
            return experiment_from_dict(obj)
        if tag == "Scenario":
            return scenario_from_dict(obj)
        if tag == "EconomyParameters":
            return economy_parameters_from_dict(obj)
        if tag == "Shock":
            return shock_from_dict(obj)
        if tag == "Equilibrium":
            return equilibrium_from_dict(obj)
        if tag == "EquilibriumResult":
            return result_from_dict(obj)
        if "__uuid__" in obj:
            return UUID(obj["__uuid__"])
        if "__datetime__" in obj:
            return datetime.fromisoformat(obj["__datetime__"])
        return {k: _decode(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_decode(item) for item in obj]
    return obj


# -- Archivos ---------------------------------------------------------------
def save_json(obj: Any, path: str | Path) -> None:
    """Serializa ``obj`` a JSON (con soporte para objetos sicm_core)."""
    if isinstance(obj, Experiment):
        payload = experiment_to_dict(obj)
    elif isinstance(obj, Scenario):
        payload = scenario_to_dict(obj)
    elif isinstance(obj, EquilibriumResult):
        payload = result_to_dict(obj)
    elif isinstance(obj, Equilibrium):
        payload = equilibrium_to_dict(obj)
    else:
        payload = obj
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, default=_default)


def load_json(path: str | Path) -> Any:
    """Carga JSON decodificando objetos sicm_core."""
    with open(path, encoding="utf-8") as fh:
        return _decode(json.load(fh))
