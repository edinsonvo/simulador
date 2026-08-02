"""Recorrido AppTest: ejecuta un experimento para cada modelo registrado."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

from sicm_core.engine.registry import registry


def check(at, label):
    if at.exception:
        raise AssertionError(f"{label}: {at.exception}")


def main():
    failures = []
    for model in registry.names():
        at = AppTest.from_file("research_lab/app.py", default_timeout=30)
        at.run()
        check(at, f"{model} arranque")
        at.sidebar.selectbox[0].set_value(model)
        at.run()
        check(at, f"{model} seleccion")
        if model in ("mundell_fleming", "islm_bp", "integrated"):
            at.sidebar.radio[1].set_value("Fijo")
            at.run()
            check(at, f"{model} regimen")
            at.sidebar.radio[1].set_value("Flexible")
            at.run()
            check(at, f"{model} regimen flexible")
        if model == "as_ad":
            at.sidebar.radio[1].set_value("Largo plazo")
            at.run()
            check(at, f"{model} horizonte")
            at.sidebar.radio[1].set_value("Corto plazo")
            at.run()
        if model == "new_classical":
            at.sidebar.radio[1].set_value("Anticipadas (P^e = P)")
            at.run()
            check(at, f"{model} expectativas")
            at.sidebar.radio[1].set_value("Sorpresa (P^e fija)")
            at.run()
        at.sidebar.button[0].click()
        at.run()
        check(at, f"{model} ejecutar")
        print(f"OK {model}")
    if failures:
        print("FALLOS:", failures)
        sys.exit(1)
    print("Todos los modelos OK")


if __name__ == "__main__":
    main()
