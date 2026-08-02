"""Entrada y salida de datos (JSON, Excel, persistencia)."""

from .json_io import (
    experiment_from_dict,
    experiment_to_dict,
    load_json,
    result_from_dict,
    result_to_dict,
    save_json,
    scenario_from_dict,
    scenario_to_dict,
)
from .persistence import ExperimentStore
from .excel_io import result_to_excel

__all__ = [
    "scenario_to_dict",
    "scenario_from_dict",
    "experiment_to_dict",
    "experiment_from_dict",
    "result_to_dict",
    "result_from_dict",
    "save_json",
    "load_json",
    "ExperimentStore",
    "result_to_excel",
]
