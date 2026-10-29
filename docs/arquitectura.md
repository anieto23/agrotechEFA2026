# Arquitectura

## Aplicación y panel

- `agrotechEFA2026/agrotechEFA2026.py` crea la aplicación Reflex y registra la página principal.
- `agrotechEFA2026/pages/dashboard.py` compone el listado de parcelas, el resumen y las vistas de parcela y sector.
- `agrotechEFA2026/state/dashboard_state.py` mantiene los datos de demostración por sesión,
  valida el alta de parcelas y los contornos de sus sectores, y calcula medias por magnitud.
- `agrotechEFA2026/components/parcel_map.py` muestra la forma de una parcela y permite abrir
  sectores rectangulares o con contorno dibujado.
- `agrotechEFA2026/components/sensor_card.py` contiene la tarjeta reutilizable de lectura.
- `agrotechEFA2026/components/colors.py` centraliza los colores usados por el panel.

El panel permite navegar e interactuar con datos ficticios en memoria; no persiste cambios ni
se conecta a la base de datos. La forma y los sectores ya están en el contrato y en `db/`; falta
conectar el panel a esas funciones. El usuario puede dibujar parcelas y sectores mediante
vértices ajustados a una cuadrícula normalizada; los sectores pueden dejar huecos, pero no
solaparse ni salir del contorno de la parcela. Esta distribución solo vive en la sesión y
reemplaza los sectores de ejemplo al confirmarla. Los dibujos no representan coordenadas
reales ni están a escala. La media de cada magnitud incluye los sectores que sí tienen una
lectura y excluye los que no tienen sensor o dato disponible.

## Base de datos

- `agrotechEFA2026/db/models.py`: tablas del contrato con **SQLModel** (lo que recomienda Reflex 0.10 para apps nuevas), tipos de medida y acciones permitidas según la parcela sea de interior o exterior.
- `agrotechEFA2026/db/session.py`: conexión. SQLite por defecto; para cambiar de motor basta `AGROTECH_DB_URL`.
- `agrotechEFA2026/db/seguridad.py`: contraseñas con PBKDF2-SHA256 y claves de aparatos con SHA-256 (solo librería estándar).
- `agrotechEFA2026/db/seed.py`: datos de ejemplo con los mismos ids que el simulador.
- `agrotechEFA2026/db/consultas.py`: funciones que usa la interfaz para leer y guardar. Cada una comprueba el permiso (dueño o técnico invitado) y valida los datos (medidas, posición dentro de la parcela, umbrales, acciones según interior o exterior).

- `agrotechEFA2026/db/lecturas.py`: valida y guarda las lecturas de los aparatos (clave del sector, tipo, unidad, rango y fecha) y crea una alerta si salen del umbral o del óptimo, sin repetirla mientras haya otra igual sin leer.

- `agrotechEFA2026/db/migrar.py` y `migrations/`: migraciones con **Alembic** sobre `SQLModel.metadata`. La app aplica las pendientes al arrancar (`actualizar_bd()`), así un cambio de tablas no borra datos. La configuración no va en un `alembic.ini` en la raíz porque Reflex usa ese nombre para su propio sistema. En SQLite se usa el modo *batch* (copia la tabla por dentro para poder cambiar columnas). Una base creada antes de las migraciones se adopta como revisión `0001` si ya tiene sectores. La `0002` añade el contorno de las parcelas dibujadas.

## API REST

`agrotechEFA2026/api/` es una app **FastAPI** que Reflex monta junto a la suya con `rx.App(api_transformer=api)` (así una sola app sirve la web y la API). Las rutas solo traducen HTTP ↔ funciones de `db/`: la lógica está en `db/` para poder probarla sin servidor. Los errores de validación se devuelven como `{"detail": "<texto>"}`, como pide el contrato.

Decisiones: la parcela guarda superficie y forma, y sus **sectores persistentes** son rectangulares (en % del plano), cada uno con su cultivo y como mucho un sensor de cada tipo; una parcela dibujada guarda su contorno como lista de vértices en % (JSON), sin cruces; los sensores de un sector comparten la clave de su aparato; las fechas se guardan en UTC con zona horaria; los rangos óptimos de cultivo van en tabla aparte y con fuente obligatoria (no se inventan). La maqueta de panel también permite dibujar sectores poligonales temporalmente, pero todavía no los guarda en la base de datos. Las tablas no validan rangos: lo harán las funciones de acceso y la API.
