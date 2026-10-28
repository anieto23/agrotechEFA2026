# Contrato de datos y API (borrador para aprobar)

> Lo redacta A. **Afecta a todos:** se comenta en el grupo y se aprueba en el PR antes de programar sobre él. Después, cualquier cambio va por PR y con aviso.
> Basado en `docs/BASES-RETO.md` (tablas y endpoints sugeridos), `docs/IDEA-PROYECTO.md` (plano, cultivos, control) y el simulador de D (`scripts/gen_sample_data.py`).

## Decisiones
- **Motor:** SQLite en desarrollo (`sqlite:///agrotech.db`, git ya lo ignora). Para publicar se puede pasar a MySQL/MariaDB cambiando `db_url`, sin tocar el código.
- **Migraciones:** cada cambio de tablas va con su migración en `migrations/versions/` (`python -m agrotechEFA2026.db.migrar nueva "..."`), en el mismo PR que el cambio de `db/models.py`.
- **Librería:** **SQLModel directamente** (`SQLModel`, `create_engine`, `Session`), como recomienda la documentación de Reflex 0.10 para apps nuevas (`rx.Model` queda como forma antigua). Se instala con `reflex[db]`, que trae SQLModel y Alembic para las migraciones.
- **Nombres:** tablas, columnas y JSON **en inglés**, como las bases y el simulador. El código Python (funciones, variables, comentarios) **en español**, como el resto del repo.
- **Fechas:** ISO 8601. Se guardan **en UTC**. Si una fecha llega sin zona horaria (`2026-10-26T12:00:00`), se entiende como **UTC** (el simulador ya manda la zona; un ESP32 con NTP da UTC). Una lectura sin `timestamp` toma la hora del servidor, y una con más de 5 minutos en el futuro se rechaza (`422`).
- **Ids:** enteros autoincrementales (el simulador ya usa enteros).
- **Sector y sensor:** un **sector** es una zona rectangular de la parcela, como las dibuja el panel de B (posición en % del plano), con su cultivo. Tiene **como mucho un sensor de cada tipo** y todos comparten la clave del aparato del sector (p. ej. un ESP32 con varias sondas). Al pulsar un sector se ven sus magnitudes comparadas con el óptimo de su cultivo. Al crear una parcela se crea su «Sector 1», que la ocupa entera; luego se divide por la mitad en vertical u horizontal.

## Tipos de medida
Lo que llega fuera del rango válido se rechaza con `422`.

| `type` | `unit` | Rango válido |
|---|---|---|
| `temperature` | `ºC` | -10 a 50 |
| `air_humidity` | `%` | 0 a 100 |
| `soil_moisture` | `%` | 0 a 100 |
| `light` | `lx` | 0 a 120000 |

## Tablas
`PK` = clave primaria, `FK` = referencia a otra tabla. Todas tienen `id` (int, PK).

**users**: `username` (str, único) · `password_hash` (str, nunca en claro) · `role` (`farmer` agricultor | `technician` técnico, que solo lee) · `created_at` (datetime).

**parcels**: `owner_id` (FK users) · `name` (str) · `kind` (`indoor` invernadero | `outdoor` campo) · `area_m2` (float > 0) · `shape` (`rectangle` | `square` | `circle` | `polygon`) · `location` (str, opcional) · `lat`, `lon` (float, opcionales) · `created_at`.

**parcel_viewers**: `parcel_id` (FK parcels) · `user_id` (FK users). Dice qué técnicos pueden ver una parcela que no es suya.

**crops** (cultivos): `name` (str, único: `tomate`, `aguacate`, `mango`, `chirimoya`…) · `description` (str).

**crop_ranges** (óptimos por cultivo y magnitud): `crop_id` (FK crops) · `type` (tipo de medida) · `optimal_min`, `optimal_max` (float) · `source` (str, **obligatorio**: de dónde sale el dato). Único por (`crop_id`, `type`). Se usa una tabla aparte para poder añadir magnitudes nuevas sin cambiar el esquema.

**sectors** (zonas de la parcela): `parcel_id` (FK parcels) · `name` (str: «Sector 1», «Sector 2»…) · `crop_id` (FK crops, opcional: vacío = sin cultivo) · `left_pct`, `top_pct`, `width_pct`, `height_pct` (float, % del plano desde la esquina superior izquierda) · `api_key_hash` (str: la clave del aparato se guarda con hash) · `active` (bool).

**sensors**: `sector_id` (FK sectors) · `type` · `unit` · `description` (str) · `threshold_low`, `threshold_high` (float, opcionales: si están vacíos se usan los óptimos del cultivo del sector) · `active` (bool). Único por (`sector_id`, `type`).

**sensor_data**: `sensor_id` (FK sensors) · `timestamp` (datetime UTC) · `value` (float) · `raw` (str JSON, opcional). Índice por (`sensor_id`, `timestamp`).

**alerts**: `sensor_id` (FK sensors) · `timestamp` · `type` (`LOW` | `HIGH`) · `message` (str) · `acknowledged` (bool).

**actions** (órdenes desde la app): `parcel_id` (FK parcels) · `user_id` (FK users) · `type` (ver abajo) · `duration_min` (int, opcional) · `status` (`pending` | `done` | `failed`) · `created_at` · `done_at` (opcional).

### Acciones permitidas según el tipo de parcela
| `type` | `indoor` | `outdoor` |
|---|---|---|
| `irrigation` (riego) | sí | sí |
| `shading` (sombreo) | sí | sí |
| `ventilation` (ventilación) | sí | no |
| `heating` (calefacción) | sí | no |
| `misting` (nebulización) | sí | no |

Si se pide una acción que no vale para esa parcela, la API responde `422` y la interfaz ni siquiera muestra el botón. Solo `farmer` puede crear acciones.

## Endpoints (API REST, prefijo `/api`)
Auth: `Authorization: Bearer <token>` salvo donde se indica.

| Método y ruta | Quién | Qué hace |
|---|---|---|
| `POST /auth/login` | todos (sin token) | `{username, password}` → `{token, role}` |
| `GET /parcels` | farmer, technician | Parcelas que puede ver el usuario |
| `GET /parcels/{id}` | farmer, technician | Parcela con sus sectores, sensores y última lectura |
| `GET /parcels/{id}/sensors` | farmer, technician | Sensores de la parcela (lista plana, como en las bases) |
| `POST /sensors/{sensor_id}/data` | aparato (cabecera `X-API-Key`, sin token) | Guarda una lectura y evalúa las alertas |
| `GET /sensors/{sensor_id}/data?from=&to=&limit=` | farmer, technician | Histórico (`limit` por defecto 500, máximo 5000) |
| `GET /dashboard` | farmer, technician | Última lectura por sensor, estado frente al óptimo y alertas sin leer |
| `GET /crops` | farmer, technician | Cultivos con sus rangos óptimos |
| `POST /parcels/{id}/actions` | farmer | `{type, duration_min}` → acción en `pending` |
| `GET /parcels/{id}/actions?status=pending` | aparato o simulador (`X-API-Key` de un sector de la parcela) | Acciones por ejecutar |
| `PATCH /actions/{id}` | aparato o simulador (`X-API-Key`) | `{status: "done" \| "failed"}` |
| `WS /ws/parcels/{id}` | opcional | Lecturas en tiempo real |

**Errores:** `401` sin token o clave incorrecta · `403` rol sin permiso o parcela ajena · `404` no existe · `422` datos no válidos (tipo, rango, fecha, acción no permitida). El cuerpo siempre es `{"detail": "<motivo en español>"}`.

### Ejemplos
`POST /api/sensors/3/data` con `X-API-Key: <clave del sector>` (es lo que ya envía el simulador):
```json
{"sensor_id": 3, "timestamp": "2026-10-26T12:34:56Z", "type": "soil_moisture", "value": 31.5, "unit": "%"}
```
Respuesta `201`:
```json
{"id": 1024, "sensor_id": 3, "timestamp": "2026-10-26T12:34:56Z", "value": 31.5, "alert": {"type": "LOW", "message": "Humedad del suelo 31.5 %, por debajo de lo recomendado (40-70 %)"}}
```
`alert` es `null` si el valor está dentro del rango. Mientras haya una alerta igual sin leer no se crea otra: se devuelve la que ya existe. En el cuerpo solo `value` es obligatorio; `type`, `unit` y `sensor_id`, si llegan, deben coincidir con el sensor.

Lectura del histórico, `GET /api/sensors/3/data?limit=1`:
```json
[{"sensor_id": 3, "timestamp": "2026-10-26T12:34:56Z", "type": "soil_moisture", "value": 31.5, "unit": "%"}]
```

Estado frente al óptimo (dentro de `GET /parcels/{id}` y `GET /dashboard`):
```json
{"sensor_id": 3, "type": "soil_moisture", "value": 31.5, "unit": "%", "optimal_min": 40, "optimal_max": 70, "status": "low"}
```
`status` puede ser `low`, `ok`, `high`, `no_data` (sin lecturas) o `no_range` (sin umbral ni óptimo con el que comparar, p. ej. mientras falten las fuentes de los cultivos). La interfaz lo muestra con texto e icono, no solo con color.

## Funciones de `db/` para B, C y E
La interfaz de Reflex llama a estas funciones directamente (no pasa por la API). Todas reciben el `usuario_id` y solo devuelven lo que ese usuario puede ver.

```python
# db/consultas.py
listar_parcelas(usuario_id: int) -> list[Parcel]
obtener_parcela(usuario_id: int, parcela_id: int) -> Parcel | None
crear_parcela(usuario_id: int, nombre: str, tipo: str, area_m2: float, forma: str) -> Parcel   # crea también su «Sector 1»
eliminar_parcela(usuario_id: int, parcela_id: int) -> None   # borra sectores, sensores, lecturas, alertas y acciones
listar_sectores(usuario_id: int, parcela_id: int) -> list[Sector]
dividir_sector(usuario_id: int, sector_id: int, orientacion: str) -> tuple[Sector, Sector]   # "vertical" | "horizontal"; (el de antes, el nuevo)
cambiar_cultivo(usuario_id: int, sector_id: int, cultivo_id: int | None) -> Sector   # None = sin cultivo
generar_clave_sector(usuario_id: int, sector_id: int) -> str   # clave para el aparato; se muestra una vez y anula la anterior
crear_sensor(usuario_id: int, sector_id: int, tipo: str, umbral_bajo: float | None, umbral_alto: float | None) -> Sensor
ultimas_lecturas(usuario_id: int, parcela_id: int) -> list[EstadoSensor]   # valor + óptimo + status
historico(usuario_id: int, sensor_id: int, desde: datetime, hasta: datetime, limite: int = 500) -> list[SensorData]
listar_cultivos() -> list[CultivoConRangos]
alertas_pendientes(usuario_id: int) -> list[Alert]
marcar_alerta_leida(usuario_id: int, alerta_id: int) -> None
crear_accion(usuario_id: int, parcela_id: int, tipo: str, duracion_min: int | None) -> Action
```
Si los datos no son válidos o el usuario no tiene permiso, lanzan `ValueError` o `PermissionError` con un mensaje en español, listo para mostrarlo en pantalla.

Uso desde un `State` de Reflex (ejemplo):
```python
from agrotechEFA2026.db import consultas

try:
    self.parcelas = consultas.listar_parcelas(self.usuario_id)
except (ValueError, PermissionError) as error:
    self.error = str(error)
```
`EstadoSensor` y `CultivoConRangos` usan los mismos nombres de campo que el JSON de la API. En `historico`, una fecha sin zona horaria se entiende como UTC. Solo el agricultor dueño puede crear, dividir, borrar, marcar alertas o dar órdenes; el técnico solo lee.

**Para el panel de B:** las formas se guardan en inglés (`rectangle`, `square`, `circle`, `polygon`) y el panel muestra su etiqueta («Rectángulo»…). El cultivo es `crop_id` (de `listar_cultivos()`); «Sin cultivo» es `None`. El formulario de parcela tiene que pedir también **interior o exterior**: decide qué acciones de control se ofrecen.

## Datos de ejemplo (`db/seed.py`)
- 2 usuarios: un agricultor y un técnico (contraseñas de prueba en `.env.example`, guardadas con hash).
- 3 parcelas, como en el simulador: «Invernadero tomates» (`indoor`), «Aguacates» y «Mangos» (`outdoor`).
- 1 sector por parcela (la ocupa entera) con 4 sensores (uno por magnitud). Los ids salen como los que ya usa el simulador: parcela 1 → sensores 1-4, parcela 2 → 5-8, parcela 3 → 9-12.
- Cultivos: tomate, aguacate, mango y chirimoya. **Los rangos óptimos se rellenan cuando tengamos fuentes fiables** (profesorado de agraria, FAO, La Palma). Hasta entonces se marcan con `source = "PENDIENTE"` y la interfaz lo indica.

## Pendiente de decidir en el grupo
1. ¿Basta con el reparto «agricultor actúa, técnico solo mira», o hace falta un administrador?
2. ¿Quién consigue las fuentes de los rangos óptimos y para cuándo?
