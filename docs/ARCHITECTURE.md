# SICM v5.1 — Arquitectura

**Autor:** Edinson Patrocinio Valencia Omaña · **Universidad Nacional de Colombia —
Sede Medellín** · edvalenciao@unal.edu.co · github.com/edinsonvo

## Filosofía

El motor ya no ejecuta modelos: ejecuta **experimentos**. El flujo global es:

```
Sidebar → Scenario → Experiment → Engine → Result → Dashboard
```

## Paquetes

```
sicm/
├── sicm_core/          Biblioteca reutilizable (sin dependencias de UI)
│   ├── engine/         Registry (registro), Dispatcher (despacho), Engine (motor)
│   ├── models/         BaseModel + keynesian (IS-LM, Mundell-Fleming) + classical
│   ├── experiments/    Scenario, Shock, Experiment, EconomyParameters
│   ├── results/        Equilibrium, Metrics, Interpretation, Transmission
│   ├── analysis/       shocks, policy, sensitivity
│   └── io/             json_io, excel_io, persistence (ExperimentStore)
├── research_lab/       Interfaz Streamlit + visualización + reportes
├── tests/              Suite de pruebas (pytest)
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

## Extensiones previstas (milestones 2-4)

- Comparación entre escenarios y historial de experimentos (ExperimentStore).
- Simulaciones por lotes y Monte Carlo.
- Calibración econométrica y sensibilidad.
- Cuatro planos sincronizados y animaciones en el Research Lab.
- Exportación completa (JSON, Excel, PDF).

## Calibraciones de referencia

Cada modelo define sus parámetros por defecto calibrados para valores
realistas (ver `sicm_core/experiments/scenario.py` → `_DEFAULTS_BY_MODEL`).
Las verificaciones numéricas de los resultados de referencia viven en
`tests/`.
