# SICM — Arquitectura

**Autor:** Edinson Patrocinio Valencia Omaña · **Universidad Nacional de
Colombia — Sede Medellín** · edvalenciao@unal.edu.co · github.com/edinsonvo

## Filosofía

El motor no ejecuta modelos: ejecuta **experimentos**. El flujo global es:

```
Sidebar → Scenario → Experiment → Engine → Result → Dashboard
```

El código está separado en dos paquetes complementarios:

- **`sicm_core`** — biblioteca reutilizable sin dependencias de interfaz.
- **`research_lab`** — interfaz Streamlit, visualización y reportes.

## Paquetes

```
sicm/
├── sicm_core/          Biblioteca reutilizable (sin dependencias de UI)
│   ├── engine/         registry (alta de modelos), dispatcher, engine, errors
│   ├── models/         BaseModel + keynesian + classical + labor + integrado
│   │   └── four_quadrant.py   equilibrio general IS-LM · AD-AS · trabajo
│   ├── experiments/    Scenario, Shock, Experiment, EconomyParameters
│   ├── results/        Equilibrium, Metrics, Interpretation, Transmission
│   ├── analysis/       shocks, policy, sensitivity
│   └── io/             json_io, excel_io, persistence (ExperimentStore)
├── research_lab/       Interfaz Streamlit + visualización + reportes
│   ├── ui/             controles del sidebar (parámetros, choques, régimen)
│   ├── visualization/  gráficas plotly (curvas, comparación, cuatro cuadrantes)
│   └── reports/        generación de PDF (reportlab) y Excel
├── tests/              Suite de pruebas (pytest · cobertura ~90 %)
├── scripts/            utilidades (apptest_all_models.py)
├── examples/           Ejemplos ejecutables (CLI)
└── docs/               Documentación
```

## Objetos centrales

### Scenario

Describe el contexto económico: modelo, parámetros, choques y metadatos.

```python
scenario = default_scenario("islm").with_shocks(Shock("G", 0.10))
```

### Experiment

Unidad de trabajo: envuelve un Scenario y guarda el resultado.

```python
experiment = new_experiment(name="Fiscal +10%", scenario=scenario)
engine.run(experiment)   # rellena experiment.result y experiment.status
```

### EquilibriumResult

Deja de ser una estructura numérica plana:

```python
result.equilibrium      # estado final
result.baseline         # estado de referencia
result.metrics          # deltas, cambios relativos, multiplicadores
result.interpretation   # lectura económica en lenguaje natural
result.transmission     # canales de transmisión
result.plots            # identificadores de figuras
```

## Registro de modelos

Los modelos se dan de alta con el decorador `@register` y no requieren
modificaciones del motor. Para añadir un modelo:

```python
@register
class MiModelo(BaseModel):
    name = "mi_modelo"
    family = "keynesian"
    label = "Mi Modelo"

    def solve(self) -> Equilibrium: ...
```

El catálogo de choques se declara en `sicm_core/analysis/shocks.py` y los
canales de transmisión en `sicm_core/results/transmission.py`.

## Robustez del motor

- `solve_1d` (`models/solvers.py`) valida el intervalo, detecta cruces de la
  función y usa un **fallback por minimización** cuando no hay cruce
  (tangencias), con mensajes de error descriptivos.
- `engine/errors.py` define `SimulationError` y `validate_parameters`, que
  rechaza parámetros NaN/inf antes de resolver.
- `Engine.run` valida parámetros y envuelve cualquier fallo inesperado en un
  `SimulationError` legible; la app lo muestra como `st.error` sin traceback.

## Calidad y CI/CD

- **GitHub Actions** (`.github/workflows/ci.yml`): tests en Python 3.11/3.12
  con cobertura mínima del 90 %, smoke test de la app (12 modelos vía
  AppTest) y lint/format con ruff 0.16.
- **Pre-commit** (`.pre-commit-config.yaml`): `ruff check` + `ruff format`.
- **Dependencias fijadas**: `requirements.txt` (runtime) y
  `requirements-dev.txt` (pytest, ruff, pytest-cov).

## Calibraciones de referencia

Cada modelo define sus parámetros por defecto calibrados para valores
realistas (ver `sicm_core/experiments/scenario.py` → `_DEFAULTS_BY_MODEL`).
Las verificaciones numéricas de los resultados de referencia viven en
`tests/`.
