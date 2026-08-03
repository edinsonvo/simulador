# SICM — Simulador Integral de Choques Macroeconómicos

[![CI](https://github.com/edinsonvo/simulador/actions/workflows/ci.yml/badge.svg)](https://github.com/edinsonvo/simulador/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Research Lab**: plataforma macroeconómica reutilizable separada en
`sicm_core` (biblioteca) y `research_lab` (interfaz Streamlit).

**Autor:** Edinson Patrocinio Valencia Omaña · **Universidad Nacional de
Colombia — Sede Medellín** · [edvalenciao@unal.edu.co](mailto:edvalenciao@unal.edu.co) ·
[github.com/edinsonvo](https://github.com/edinsonvo)

## Modelos incluidos (12)

| Modelo            | Familia       | Régimen              | Resultados verificados |
|-------------------|---------------|----------------------|------------------------|
| IS-LM             | Keynesiano    | Cerrada              | multiplicadores, crowding-out |
| Mundell-Fleming   | Keynesiano    | Flexible / Fijo      | efectividad de políticas por régimen |
| OA-DA (AS-AD)     | Keynesiano    | Corto / largo plazo  | pendientes de la Phillips, neutralidad en largo plazo |
| IS-LM-BP          | Keynesiano    | Perfecta movilidad   | transmisión monetaria/fiscal con flujos de capital |
| Clásico cerrado   | Clásico       | Pleno empleo         | neutralidad del dinero, crowding-out |
| Clásico abierto   | Clásico       | r = r_w              | crowding vía NX, neutralidad |
| Clásico nuevo     | Clásico       | Expectativas         | curva de Lucas, sorpresas de precios |
| Neokeynesiano     | Neokeynesiano | Regla de Taylor      | 3 ecuaciones, política monetaria |
| Okun              | Laboral       | Mercado laboral      | ley de Okun, gap y desempleo |
| Phillips          | Laboral       | Mercado laboral      | curva de Phillips, expectativas |
| Integrado         | Integrado     | 4 planos             | sistema simultáneo de bienes/dinero/trabajo/externo |
| Cuatro cuadrantes | General       | IS-LM · AD-AS · Trabajo | equilibrio general con salarios y expectativas |

## Estructura

```
sicm/
├── pyproject.toml · requirements.txt · requirements-dev.txt · LICENSE · README.md
├── .github/workflows/ci.yml    CI: tests + cobertura + app + lint
├── .pre-commit-config.yaml     hooks ruff (check + format)
├── sicm_core/                  modelos, motor, experimentos, análisis, resultados, I/O
├── research_lab/               aplicación Streamlit, visualización y reportes
├── tests/                      suite de pruebas (231 tests · cobertura ~90 %)
├── scripts/                    utilidades (apptest_all_models.py)
├── examples/                   ejemplos ejecutables
└── docs/                       documentación de arquitectura
```

## Instalación

```bash
pip install -r requirements-dev.txt   # runtime + dev (pytest, ruff, pytest-cov)
# o mínimo para ejecutar:
pip install -r requirements.txt
pytest                                 # suite de pruebas con cobertura
streamlit run research_lab/app.py      # interfaz
```

## Calidad

- **Tests:** 231 pruebas (`pytest`), cobertura mínima **90 %** en CI.
- **Lint y formato:** `ruff check sicm_core research_lab tests scripts` y
  `ruff format --check ...` (hook de pre-commit).
- **Smoke test de la app:** `python scripts/apptest_all_models.py` recorre
  los 12 modelos con `streamlit.testing.AppTest`.

## Flujo de uso (CLI)

```bash
python examples/run_experiment.py islm --shock G --pct 10
```

## Estado del proyecto

- **Milestone 1 — infraestructura:** motor, registro, escenarios, experimentos,
  resultados ricos, análisis e I/O. ✅
- **Milestone 2 — núcleo económico:** 12 modelos (keynesiano, clásico,
  neokeynesiano, laboral, integrado, cuatro cuadrantes). ✅
- **Milestone 3 — Research Lab:** dashboard, laboratorio de sensibilidad,
  almacén de experimentos y exportación (PDF, Excel, JSON). ✅
- **Milestone 4 — robustez y CI/CD:** errores legibles, validación de
  parámetros, GitHub Actions, dependencias fijadas y pre-commit. ✅
