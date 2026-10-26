# Evolución del trabajo

Registro de cómo ha ido creciendo el proyecto, como piden las bases del reto. Lo más reciente, arriba.
**Cada PR añade aquí una línea** (fecha, quién, qué y número de PR). El detalle está en el historial de GitHub.

## 26-oct-2026
- **efapro (A, datos):** API REST con FastAPI dentro de Reflex; primera ruta: entrada de lecturas de los sensores con clave del aparato, validación y alertas. Probada con el simulador: 1164 de 1164 lecturas guardadas. 65 tests.
- **efapro (A, datos):** se crea este registro y la regla de que cada PR añada su línea (`AGENTS.md`). (PR #9)
- **efapro (A, datos):** funciones de acceso a datos para la interfaz, con permisos por usuario y validación (posición dentro de la parcela, umbrales, acciones según interior o exterior). 50 tests. (PR #8)
- **efapro (A, datos):** base de datos con SQLModel: tablas del contrato, conexión, contraseñas y claves con hash y datos de ejemplo con los mismos ids que el simulador. Se corrige la versión de Python pedida (3.15 → 3.11+) y se completan las dependencias. (PR #7)
- **efapro (A, datos):** borrador del contrato de datos y API (`docs/contrato.md`): tablas, endpoints, funciones para la interfaz. (PR #6)
- **efapro:** idea del producto, fases y cosas a tener en cuenta (`docs/IDEA-PROYECTO.md`). (PR #5)
- **anieto23 (B, panel):** la maqueta del panel se separa en página, tarjeta reutilizable y colores; primer `docs/arquitectura.md`. (PR #4)

## 23-oct-2026
- **efapro:** forma de trabajar del equipo: rama corta por tarea, cada uno une su PR, guía de git para principiantes e instrucciones para las IAs. (PR #1, #3)
- **mhjosemi (D, sensores):** simulador de sensores con datos realistas de la Costa Tropical y sus tests (PR #2); scripts de prueba de avisos por Telegram.
- **mhjosemi:** guiones por persona y plan de equipo.
- **anieto23 (B, panel):** primera interfaz de prueba del panel, colores para tema oscuro y logo de Agrotech.

## 22-oct-2026
- **anieto23:** se crea el repositorio y se inicializa el proyecto con Reflex.
