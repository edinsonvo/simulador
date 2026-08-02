"""Persistencia de experimentos en el sistema de archivos."""

from __future__ import annotations

import tempfile
from pathlib import Path
from uuid import UUID

from ..experiments.experiment import Experiment
from .json_io import experiment_from_dict, experiment_to_dict, load_json, save_json


class ExperimentStore:
    """Almacén de experimentos en JSON (un archivo por experimento).

    Las escrituras son atómicas (archivo temporal + rename) para no
    corromper el almacén ante interrupciones.
    """

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # -- Rutas ---------------------------------------------------------------
    def _path_for(self, experiment_id: str | UUID) -> Path:
        return self.base_dir / f"{experiment_id}.json"

    # -- Escritura -----------------------------------------------------------
    def save(self, experiment: Experiment) -> None:
        payload = experiment_to_dict(experiment)
        target = self._path_for(experiment.id)
        fd, tmp = tempfile.mkstemp(dir=self.base_dir, suffix=".tmp")
        try:
            import json

            with open(fd, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=2)
            tmp_path = Path(tmp)
            tmp_path.replace(target)
        finally:
            leftover = Path(tmp)
            if leftover.exists():
                leftover.unlink()

    def save_many(self, experiments: list[Experiment]) -> None:
        for experiment in experiments:
            self.save(experiment)

    # -- Lectura -------------------------------------------------------------
    def load(self, experiment_id: str | UUID) -> Experiment:
        path = self._path_for(experiment_id)
        if not path.exists():
            raise FileNotFoundError(f"No existe el experimento '{experiment_id}'.")
        return load_json(path)

    def load_all(self) -> list[Experiment]:
        return [load_json(path) for path in sorted(self.base_dir.glob("*.json"))]

    def exists(self, experiment_id: str | UUID) -> bool:
        return self._path_for(experiment_id).exists()

    # -- Borrado -------------------------------------------------------------
    def delete(self, experiment_id: str | UUID) -> None:
        path = self._path_for(experiment_id)
        if path.exists():
            path.unlink()

    def clear(self) -> None:
        for path in self.base_dir.glob("*.json"):
            path.unlink()

    def count(self) -> int:
        return len(list(self.base_dir.glob("*.json")))
