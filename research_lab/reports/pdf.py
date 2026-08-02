"""Generación de reportes PDF a partir de resultados."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from sicm_core.branding import (
    AUTHOR,
    EMAIL,
    GITHUB,
    VERSION,
    institution_line,
    signature,
)
from sicm_core.results.equilibrium import EquilibriumResult

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "escudo_unal_color.png"


def _build_styles():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "SICMSubtitle",
            parent=styles["BodyText"],
            fontSize=11,
            leading=15,
            textColor="#555555",
            spaceAfter=6 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            "SICMHeader",
            parent=styles["BodyText"],
            fontSize=8,
            leading=11,
            textColor="#555555",
            alignment=1,
        )
    )
    return styles, A4


def _page_footer(canvas, doc):
    """Pie de página institucional en cada hoja del documento."""
    from reportlab.lib import colors
    from reportlab.lib.units import mm

    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#c8c8c8"))
    canvas.setLineWidth(0.5)
    y = 12 * mm
    canvas.line(20 * mm, y, doc.pagesize[0] - 20 * mm, y)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawCentredString(
        doc.pagesize[0] / 2.0,
        y - 4 * mm,
        f"{signature()} · {datetime.now():%Y-%m-%d %H:%M}",
    )
    canvas.setFont("Helvetica-Oblique", 7)
    canvas.drawCentredString(
        doc.pagesize[0] / 2.0,
        y - 8 * mm,
        f"{AUTHOR} · {institution_line()} · {EMAIL} · {GITHUB}",
    )
    canvas.restoreState()


def _build_header(styles):
    """Cabecera con el escudo de la Universidad y los datos de autoría."""
    from reportlab.lib.units import mm
    from reportlab.platypus import Image as RLImage
    from reportlab.platypus import Paragraph, Table, TableStyle

    if LOGO_PATH.exists():
        image = RLImage(str(LOGO_PATH), width=30 * mm, height=40 * mm)
    else:
        image = Paragraph("", styles["BodyText"])
    text = (
        f"<b>Universidad Nacional de Colombia — Sede Medellín</b><br/>"
        f"Simulador Integral de Choques Macroeconómicos (SICM) · v{VERSION}<br/>"
        f"{AUTHOR} · {EMAIL} · {GITHUB}"
    )
    header = Table([[image, Paragraph(text, styles["SICMHeader"])]],
                   colWidths=[32 * mm, 148 * mm])
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("LEFTPADDING", (1, 0), (1, -1), 10),
            ]
        )
    )
    return header


def generate_pdf_report(
    result: EquilibriumResult, path: str | Path, title: str = "Reporte SICM"
) -> Path:
    """Genera un PDF legible con los resultados del experimento."""
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    styles, pagesize = _build_styles()
    doc = SimpleDocTemplate(str(path), pagesize=pagesize)
    story: list[Any] = []

    story.append(_build_header(styles))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(title, styles["Title"]))
    story.append(Paragraph(result.interpretation.title, styles["SICMSubtitle"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Resumen", styles["Heading2"]))
    story.append(Paragraph(result.interpretation.summary, styles["BodyText"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Equilibrio", styles["Heading2"]))
    rows = [["Variable", "Base", "Final", "Δ absoluto"]]
    for key, info in result.variable_table().items():
        rows.append([
            key,
            f"{info['base']:.4f}" if info["base"] is not None else "—",
            f"{info['final']:.4f}",
            f"{info['delta']:+.4f}" if info["delta"] is not None else "—",
        ])
    table = Table(rows, colWidths=[40, 60, 60, 60])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbe7f4")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Multiplicadores", styles["Heading2"]))
    if result.metrics.multipliers:
        for key, value in result.metrics.multipliers.items():
            story.append(Paragraph(f"{key} = {value:.4f}", styles["BodyText"]))
    else:
        story.append(Paragraph("Sin choque aplicado.", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Interpretación", styles["Heading2"]))
    for bullet in result.interpretation.bullets:
        story.append(Paragraph(f"• {bullet}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Canales de transmisión", styles["Heading2"]))
    for channel in result.transmission.channels:
        story.append(Paragraph(f"• {channel}", styles["BodyText"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(result.transmission.description, styles["BodyText"]))

    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph(
        f"Documento generado por {signature()} el {datetime.now():%Y-%m-%d %H:%M}.",
        styles["SICMHeader"],
    ))

    doc.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)
    return path
