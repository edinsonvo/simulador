# Changelog

Todos los cambios notables de SICM se documentan aquí. El formato sigue
[Keep a Changelog](https://keepachangelog.com/es/1.1.0/) y el proyecto usa
[Versionado Semántico](https://semver.org/lang/es/).

## [No publicado] — 5.1.0

### Añadido
- **Robustez del motor (P1):** validación de parámetros (`validate_parameters`),
  `SimulationError` con mensajes legibles y fallback por minimización en
  `solve_1d` para funciones tangentes.
- **CI/CD (P2):** flujo de GitHub Actions (tests, cobertura, app, lint),
  pre-commit con ruff y dependencias fijadas.
- **Cobertura de pruebas (P3):** tests de choques para los 12 modelos,
  interpretación, transmisión, exportación (PDF/Excel/JSON), gráficas y
  smoke tests de la app con AppTest. Cobertura total ≈ 90 %.
- **UX (P4):** banner de resumen ejecutivo en el dashboard con las cuatro
  mayores variaciones de variables.
- `docs/ARCHITECTURE.md` y README actualizados; `CHANGELOG.md` creado.

### Cambiado
- `requirements.txt` con versiones exactas (runtime) y
  `requirements-dev.txt` (desarrollo).
- Fechas de informes y exportaciones en UTC explícito.

### Corregido
- Lint de todo el proyecto (ruff check + ruff format), incluido `open()`
  sin contexto y variables sin usar.
- `# noqa` innecesario tras acotar el `except` del solver.

## [5.1.0rc1.post3] — 2026-08-01

### Añadido
- **Modelo de equilibrio general de cuatro cuadrantes** (`four_quadrant`):
  IS-LM, AD-AS, demanda de trabajo (W/P = PMgL) y oferta de trabajo con
  salario nominal; dinámica con expectativas adaptativas de precios.
- Controles en la app para el nuevo modelo (parámetros, horizonte, choques
  de G, M, productividad y expectativas).
- Bootstrap de `sys.path` en `research_lab/app.py` para ejecutar la app desde
  el directorio de la app (Streamlit Cloud / GitHub Actions).

### Corregido
- Despliegue en Streamlit Cloud: la app ya no depende de una instalación
  editable; resuelve los paquetes del repositorio en tiempo de ejecución.

## [5.1.0rc1] — 2026-07

### Añadido
- Milestone 1 (infraestructura): motor, registro de modelos, escenarios,
  experimentos, resultados ricos (interpretación, transmisión, métricas),
  análisis (choques, políticas, sensibilidad) y I/O (JSON, Excel,
  ExperimentStore).
- Milestone 2 (núcleo económico): 12 modelos.
- Milestone 3 (Research Lab): dashboard, laboratorio de sensibilidad,
  almacén de experimentos, exportación PDF/Excel y documentación integrada.
