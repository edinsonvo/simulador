# SICM v5.1 — Simulador Integral de Choques Macroeconómicos

**Research Lab (RC1.3)**: plataforma macroeconómica reutilizable separada en
`sicm_core` (biblioteca) y `research_lab` (interfaz Streamlit).

**Autor:** Edinson Patrocinio Valencia Omaña · **Universidad Nacional de Colombia —
Sede Medellín** · [edvalenciao@unal.edu.co](mailto:edvalenciao@unal.edu.co) ·
[github.com/edinsonvo](https://github.com/edinsonvo)

## Estructura

```
sicm/
├── pyproject.toml / requirements.txt / LICENSE / README.md
├── sicm_core/        modelos, motor, experimentos, análisis, resultados, I/O
├── research_lab/     aplicación Streamlit, visualización y reportes
├── tests/            suite de pruebas
├── examples/         ejemplos ejecutables
└── docs/             documentación de arquitectura
```

## Modelos incluidos

| Modelo            | Familia    | Régimen              | Resultados verificados |
|-------------------|------------|----------------------|------------------------|
| IS-LM             | Keynesiano | Cerrada              | multiplicadores, crowding-out |
| Mundell-Fleming   | Keynesiano | Flexible / Fijo      | efectividad de políticas por régimen |
| Clásico cerrado   | Clásico    | Pleno empleo         | neutralidad del dinero, crowding-out |
| Clásico abierto   | Clásico    | r = r_w              | crowding vía NX, neutralidad |

## Instalación

```bash
pip install -r requirements.txt        # o: pip install -e .[dev]
pytest                                 # suite de pruebas
streamlit run research_lab/app.py      # interfaz
```

## Flujo de uso (CLI)

```bash
python examples/run_experiment.py islm --shock G --pct 10
```

## Estado del proyecto

- **Milestone 1 (completado):** infraestructura, motor, registro, escenarios,
  experimentos, resultados ricos, análisis y I/O.
- **Milestones 2-4 (planificados):** núcleo económico ampliado, interfaz
  avanzada (dashboard, comparador) y Research Lab (cuatro planos, Monte Carlo).
