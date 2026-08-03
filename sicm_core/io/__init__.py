"""Entrada y salida de datos (JSON, Excel, persistencia)."""

from .excel_io import result_to_excel
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

__all__ = [
    "ExperimentStore",
    "experiment_from_dict",
    "experiment_to_dict",
    "load_json",
    "result_from_dict",
    "result_to_dict",
    "result_to_excel",
    "save_json",
    "scenario_from_dict",
    "scenario_to_dict",
]
