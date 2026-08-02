"""SICM v5.1 — Simulador Integral de Choques Macroeconómicos.

Core library: models, engine, experiments, analysis, results, I/O.
"""

__version__ = "5.1.0rc1.post3"

# Importar los modelos registra las clases en el motor.
from . import models  # noqa: F401

# API pública del motor.
from .engine import Engine, dispatch, registry, register  # noqa: F401
