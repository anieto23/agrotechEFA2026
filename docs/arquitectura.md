# Arquitectura

## Aplicación y panel

- `agrotechEFA2026/agrotechEFA2026.py` crea la aplicación Reflex y registra la página principal.
- `agrotechEFA2026/pages/dashboard.py` compone la cabecera, los indicadores y el estado de la parcela.
- `agrotechEFA2026/components/sensor_card.py` contiene la tarjeta reutilizable de lectura.
- `agrotechEFA2026/components/colors.py` centraliza los colores usados por el panel.

El panel sigue siendo una maqueta: las lecturas son fijas y no hay conexión con la API,
estado dinámico ni gráficos de histórico implementados todavía.

## Base de datos

- `agrotechEFA2026/db/models.py`: tablas del contrato con **SQLModel** (lo que recomienda Reflex 0.10 para apps nuevas), tipos de medida y acciones permitidas según la parcela sea de interior o exterior.
- `agrotechEFA2026/db/session.py`: conexión. SQLite por defecto; para cambiar de motor basta `AGROTECH_DB_URL`.
- `agrotechEFA2026/db/seguridad.py`: contraseñas con PBKDF2-SHA256 y claves de aparatos con SHA-256 (solo librería estándar).
- `agrotechEFA2026/db/seed.py`: datos de ejemplo con los mismos ids que el simulador.
- `agrotechEFA2026/db/consultas.py`: funciones que usa la interfaz para leer y guardar. Cada una comprueba el permiso (dueño o técnico invitado) y valida los datos (medidas, posición dentro de la parcela, umbrales, acciones según interior o exterior).

- `agrotechEFA2026/db/lecturas.py`: valida y guarda las lecturas de los aparatos (clave del nodo, tipo, unidad, rango y fecha) y crea una alerta si salen del umbral o del óptimo, sin repetirla mientras haya otra igual sin leer.

## API REST

`agrotechEFA2026/api/` es una app **FastAPI** que Reflex monta junto a la suya con `rx.App(api_transformer=api)` (así una sola app sirve la web y la API). Las rutas solo traducen HTTP ↔ funciones de `db/`: la lógica está en `db/` para poder probarla sin servidor. Los errores de validación se devuelven como `{"detail": "<texto>"}`, como pide el contrato.

Decisiones: un **nodo** es el aparato del plano y agrupa sensores de una magnitud cada uno; las fechas se guardan en UTC con zona horaria; los rangos óptimos de cultivo van en tabla aparte y con fuente obligatoria (no se inventan). Las tablas no validan rangos: lo harán las funciones de acceso y la API.
