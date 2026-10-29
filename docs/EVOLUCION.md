# Evolución del trabajo

Registro de cómo ha ido creciendo el proyecto, como piden las bases del reto. Lo más reciente, arriba.
**Cada PR añade aquí una línea** (fecha, quién, qué y número de PR). El detalle está en el historial de GitHub.

## 29-oct-2026
- **rmolino23-art (C, gestión):** marco común de la app (`components/layout.py`): barra lateral en ordenador, barra inferior en móvil, cabecera con usuario, rol e indicador de alertas, e interruptor claro/oscuro que usa los colores de `colors.py`. Páginas vacías de Parcelas, Sensores y Alertas ya con el menú. Probado en ordenador y a 375 px. 126 tests. (PR #22)
- **anieto23 (B, panel):** completa el registro histórico con los cambios de los PR #14–#18.
- **anieto23 (B, panel):** mejora del dibujo manual: los puntos coinciden con la cuadrícula, se distinguen los seleccionados, se mantiene visible la cuadrícula completa al dibujar sectores, se puede abrir cualquier sector y sus nombres quedan centrados. También se mejora la visibilidad de los bordes. (PR #18)
- **anieto23 (B, panel):** dibujo libre de sectores poligonales dentro de las parcelas, con validación para evitar solapamientos y sectores fuera del contorno. Los sectores dibujados se conservan al navegar por el panel durante la sesión. (PR #17)

## 28-oct-2026
- **efapro (A, datos):** la base de datos guarda el contorno de las parcelas dibujadas en el panel (forma `drawn`), con la misma validación que el panel: al menos 3 vértices, dentro del plano y sin cruces. Primera migración real (0002): la base de prueba conservó sus 1164 lecturas. 101 tests. (PR #15)
- **anieto23 (B, panel):** se añade el dibujo manual de parcelas sobre una cuadrícula, con edición de vértices, validación del contorno y actualización del panel y su documentación. (PR #14)
- **efapro (A, datos):** migraciones con Alembic: los cambios de tablas ya no borran datos; la app las aplica al arrancar y los tests avisan si alguien cambia las tablas sin su migración. Probado: añadir una columna a una copia de la base real conservó las 1164 lecturas. 83 tests. (PR #13)
- **efapro (A, datos):** la base de datos se adapta al panel de B: la parcela guarda superficie, forma e interior/exterior, y se divide en sectores con su cultivo y sus sensores. Nuevas funciones para el panel: listar, dividir y cambiar el cultivo de un sector, borrar una parcela con todo lo suyo y generar la clave del aparato de un sector. 77 tests. (PR #12)
- **anieto23 (B, panel):** maqueta del panel con varias parcelas, formas y sectores que se dividen, con cultivo y sensores por sector. (PR #11)

## 28-oct-2026 (D)
- **mhjosemi (D, sensores):** servicios de riego recomendado y avisos; bot de Telegram conectado a la base de datos que informa del estado de parcelas y avisa de nuevas alertas solo al chat configurado en `.env`; exportación CSV/PDF, firmware ESP32, simulador virtual, Docker, documentación y pruebas. (PR #16)

## 27-oct-2026
- **mhjosemi (D, sensores):** recomendación de riego (`services/riego.py`, reglas por cultivo y previsión de Open-Meteo con caché), avisos por Telegram con máximo 1 cada 30 min (`services/telegram.py`), exportar CSV e informe PDF (`services/export.py`), firmware MicroPython del ESP32 y ESP32 virtual como plan B, `docs/hardware.md` y `Dockerfile`. Cifras de cultivos pendientes de validar con el profesorado agrario.

## 26-oct-2026
- **efapro (A, datos):** API REST con FastAPI dentro de Reflex; primera ruta: entrada de lecturas de los sensores con clave del aparato, validación y alertas. Probada con el simulador: 1164 de 1164 lecturas guardadas. 65 tests. Las IAs del equipo comprueban ahora el entorno (Python, dependencias y tests) cada vez que traen lo de los demás. (PR #10)
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
