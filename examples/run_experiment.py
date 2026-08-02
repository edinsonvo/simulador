"""Ejemplo completo del flujo: Scenario → Experiment → Engine → Result.

Uso:
    python examples/run_experiment.py [modelo] [--shock G|M|T|r_w|Yn] [--pct 10]

    python examples/run_experiment.py islm --shock G --pct 10
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sicm_core import Engine, registry  # noqa: E402
from sicm_core.analysis.shocks import shocks_for  # noqa: E402
from sicm_core.experiments import default_scenario, new_experiment  # noqa: E402
from sicm_core.experiments.scenario import Shock  # noqa: E402
from sicm_core.io import result_to_excel, save_json  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta un experimento SICM.")
    parser.add_argument("model", nargs="?", default="islm",
                        choices=list(registry.names()))
    parser.add_argument("--shock", default=None,
                        help="Parámetro objetivo del choque (p. ej. G, M, T).")
    parser.add_argument("--pct", type=float, default=10.0,
                        help="Magnitud del choque en porcentaje.")
    args = parser.parse_args()

    scenario = default_scenario(args.model)
    if args.shock:
        scenario = scenario.with_shocks(
            Shock(args.shock, args.pct / 100.0,
                  description=f"cambio de {args.shock} en {args.pct:.0f}%")
        )

    experiment = new_experiment(
        name=f"{args.model} · {args.shock or 'base'}",
        scenario=scenario,
        author="ejemplo-cli",
    )
    engine = Engine()
    result = engine.run(experiment)

    print(f"== {result.interpretation.title} ==")
    print(f"Dirección: {result.interpretation.direction}")
    print()
    print(f"{'Variable':<6} {'Base':>12} {'Final':>12} {'Δ':>12}")
    for key, info in result.variable_table().items():
        base = f"{info['base']:.4f}" if info["base"] is not None else "—"
        delta = f"{info['delta']:+.4f}" if info["delta"] is not None else "—"
        print(f"{key:<6} {base:>12} {info['final']:>12.4f} {delta:>12}")
    print()
    for bullet in result.interpretation.bullets:
        print(f"• {bullet}")

    out_dir = Path(__file__).resolve().parent / "out"
    out_dir.mkdir(exist_ok=True)
    json_path = out_dir / f"experiment_{experiment.id}.json"
    save_json(experiment, json_path)
    print(f"\nResultado guardado en: {json_path}")

    excel_path = out_dir / "resultado.xlsx"
    result_to_excel(result, excel_path)
    print(f"Excel exportado en: {excel_path}")


if __name__ == "__main__":
    main()
