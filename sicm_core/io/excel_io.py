"""Exportación de resultados a Excel."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from ..branding import (
    AUTHOR,
    CAMPUS,
    EMAIL,
    GITHUB,
    INSTITUTION,
    VERSION,
    institution_line,
    signature,
)
from ..results.equilibrium import EquilibriumResult

_VAR_LABELS = {
    "Y": "Producto (Y)",
    "r": "Tasa de interés (r)",
    "P": "Nivel de precios (P)",
    "e": "Tipo de cambio (e)",
    "M": "Oferta monetaria (M)",
    "NX": "Exportaciones netas (NX)",
    "BP": "Balance de pagos (BP)",
    "C": "Consumo (C)",
    "I": "Inversión (I)",
    "S": "Ahorro (S)",
}


def _variable_frame(result: EquilibriumResult) -> pd.DataFrame:
    rows = []
    for key, info in result.variable_table().items():
        rows.append(
            {
                "Variable": key,
                "Descripción": _VAR_LABELS.get(key, ""),
                "Base": info["base"],
                "Final": info["final"],
                "Δ absoluto": info["delta"],
            }
        )
    return pd.DataFrame(rows)


def _branding_frame() -> pd.DataFrame:
    generated = datetime.now()
    return pd.DataFrame(
        {
            "Campo": [
                "Herramienta",
                "Autor",
                "Institución",
                "Correo",
                "GitHub",
                "Versión",
                "Fecha de generación",
            ],
            "Valor": [
                signature(),
                AUTHOR,
                institution_line(),
                EMAIL,
                GITHUB,
                VERSION,
                f"{generated:%Y-%m-%d %H:%M}",
            ],
        }
    )


def result_to_excel(result: EquilibriumResult, path: str | Path) -> Path:
    """Exporta un resultado a un libro de Excel con varias hojas."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metrics = result.metrics

    equilibrium_df = _variable_frame(result)
    multipliers_df = pd.DataFrame(
        [{"Multiplicador": k, "Valor": v} for k, v in metrics.multipliers.items()]
    )
    deltas_df = pd.DataFrame(
        [{"Variable": k, "Δ absoluto": v, "Δ relativo (%)": metrics.relative_changes.get(k) * 100 if metrics.relative_changes.get(k) is not None else None} for k, v in metrics.deltas.items()]
    )
    interpretation_df = pd.DataFrame(
        {
            "Campo": ["Título", "Dirección", "Resumen"],
            "Valor": [
                result.interpretation.title,
                result.interpretation.direction,
                result.interpretation.summary,
            ],
        }
    )
    transmission_df = pd.DataFrame(
        {
            "Canal": result.transmission.channels,
            "Descripción": result.transmission.description,
        }
    )
    branding_df = _branding_frame()

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        branding_df.to_excel(writer, sheet_name="Acerca de", index=False)
        equilibrium_df.to_excel(writer, sheet_name="Equilibrio", index=False)
        deltas_df.to_excel(writer, sheet_name="Variaciones", index=False)
        multipliers_df.to_excel(writer, sheet_name="Multiplicadores", index=False)
        interpretation_df.to_excel(writer, sheet_name="Interpretación", index=False)
        transmission_df.to_excel(writer, sheet_name="Transmisión", index=False)
        writer.book.properties.title = f"SICM — {result.interpretation.title}"
        writer.book.properties.creator = AUTHOR
        writer.book.properties.subject = institution_line()
        writer.book.properties.description = signature()
        writer.book.properties.created = datetime.now()
    return path
