"""Marca y autoría de SICM.

Constantes reutilizadas por la interfaz (``research_lab``) y por los
documentos generados (PDF, Excel).
"""

from __future__ import annotations

from . import __version__

AUTHOR = "Edinson Patrocinio Valencia Omaña"
INSTITUTION = "Universidad Nacional de Colombia"
CAMPUS = "Sede Medellín"
EMAIL = "edvalenciao@unal.edu.co"
GITHUB = "https://github.com/edinsonvo"
VERSION = __version__


def signature() -> str:
    """Firma oficial: ``SICM by <correo> · v<versión>``."""
    return f"SICM by {EMAIL} · v{VERSION}"


def institution_line() -> str:
    """Línea institucional: ``Universidad Nacional de Colombia — Sede Medellín``."""
    return f"{INSTITUTION} — {CAMPUS}"


def about_short() -> str:
    """Resumen de autoría para cabeceras y pies de página."""
    return f"{AUTHOR} · {institution_line()} · {EMAIL} · {GITHUB}"
