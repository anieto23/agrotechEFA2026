# Contrato de datos y API (borrador para aprobar)

> Lo redacta A. **Afecta a todos:** se comenta en el grupo y se aprueba en el PR antes de programar sobre él. Después, cualquier cambio va por PR y con aviso.
> Basado en `docs/BASES-RETO.md` (tablas y endpoints sugeridos), `docs/IDEA-PROYECTO.md` (plano, cultivos, control) y el simulador de D (`scripts/gen_sample_data.py`).

## Decisiones
- **Motor:** SQLite en desarrollo (`sqlite:///agrotech.db`, git ya lo ignora). Para publicar se puede pasar a MySQL/MariaDB cambiando `db_url`, sin tocar el código.
- **Librería:** **SQLModel directamente** (`SQLModel`, `create_engine`, `Session`), como recomienda la documentación de Reflex 0.10 para apps nuevas (`rx.Model` queda como forma antigua). Se instala con `reflex[db]`, que trae SQLModel y Alembic para las migraciones.
- **Nombres:** tablas, columnas y JSON **en inglés**, como las bases y el simulador. El código Python (funciones, variables, comentarios) **en español**, como el resto del repo.
- **Fechas:** ISO 8601. Se guardan **en UTC**. Si una fecha llega sin zona horaria (`2026-10-26T12:00:00`), se entiende como **UTC** (el simulador ya manda la zona; un ESP32 con NTP da UTC). Una lectura sin `timestamp` toma la hora del servidor, y una con más de 5 minutos en el futuro se rechaza (`422`).
- **Ids:** enteros autoincrementales (el simulador ya usa enteros).
- **Nodo y sensor:** un **nodo** es el aparato que se coloca en el plano (un ESP32 con varias sondas). Cada **sensor** mide una sola magnitud y pertenece a un nodo. Al pulsar un nodo en el plano se ven todas sus magnitudes comparadas con el óptimo del cultivo.

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

**parcels**: `owner_id` (FK users) · `name` (str) · `kind` (`indoor` invernadero | `outdoor` campo) · `width_m`, `length_m` (float > 0) · `location` (str, opcional) · `lat`, `lon` (float, opcionales) · `created_at`.

**parcel_viewers**: `parcel_id` (FK parcels) · `user_id` (FK users). Dice qué técnicos pueden ver una parcela que no es suya.

**crops** (cultivos): `name` (str, único: `tomate`, `aguacate`, `mango`, `chirimoya`…) · `description` (str).

**crop_ranges** (óptimos por cultivo y magnitud): `crop_id` (FK crops) · `type` (tipo de medida) · `optimal_min`, `optimal_max` (float) · `source` (str, **obligatorio**: de dónde sale el dato). Único por (`crop_id`, `type`). Se usa una tabla aparte para poder añadir magnitudes nuevas sin cambiar el esquema.

**nodes** (aparatos en el plano): `parcel_id` (FK parcels) · `name` (str) · `crop_id` (FK crops, opcional) · `pos_x_m`, `pos_y_m` (float, en metros desde la esquina superior izquierda, **dentro** de la parcela) · `radius_m` (float > 0, zona que cubre) · `api_key_hash` (str: la clave del aparato se guarda con hash) · `active` (bool).

**sensors**: `node_id` (FK nodes) · `type` · `unit` · `description` (str) · `threshold_low`, `threshold_high` (float, opcionales: si están vacíos se usan los óptimos del cultivo del nodo) · `active` (bool).

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
| `GET /parcels/{id}` | farmer, technician | Parcela con sus nodos, sensores y última lectura |
| `GET /parcels/{id}/sensors` | farmer, technician | Sensores de la parcela (lista plana, como en las bases) |
| `POST /sensors/{sensor_id}/data` | aparato (cabecera `X-API-Key`, sin token) | Guarda una lectura y evalúa las alertas |
| `GET /sensors/{sensor_id}/data?from=&to=&limit=` | farmer, technician | Histórico (`limit` por defecto 500, máximo 5000) |
| `GET /dashboard` | farmer, technician | Última lectura por sensor, estado frente al óptimo y alertas sin leer |
| `GET /crops` | farmer, technician | Cultivos con sus rangos óptimos |
| `POST /parcels/{id}/actions` | farmer | `{type, duration_min}` → acción en `pending` |
| `GET /parcels/{id}/actions?status=pending` | aparato o simulador (`X-API-Key` de un nodo de la parcela) | Acciones por ejecutar |
| `PATCH /actions/{id}` | aparato o simulador (`X-API-Key`) | `{status: "done" \| "failed"}` |
| `WS /ws/parcels/{id}` | opcional | Lecturas en tiempo real |

**Errores:** `401` sin token o clave incorrecta · `403` rol sin permiso o parcela ajena · `404` no existe · `422` datos no válidos (tipo, rango, fecha, posición fuera de la parcela, acción no permitida). El cuerpo siempre es `{"detail": "<motivo en español>"}`.

### Ejemplos
`POST /api/sensors/3/data` con `X-API-Key: <clave del nodo>` (es lo que ya envía el simulador):
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
crear_parcela(usuario_id: int, nombre: str, tipo: str, ancho_m: float, largo_m: float) -> Parcel
colocar_nodo(usuario_id: int, parcela_id: int, nombre: str, x_m: float, y_m: float, radio_m: float, cultivo_id: int | None) -> tuple[Node, str]   # str = clave del aparato, se muestra una sola vez
mover_nodo(usuario_id: int, nodo_id: int, x_m: float, y_m: float) -> Node
crear_sensor(usuario_id: int, nodo_id: int, tipo: str, umbral_bajo: float | None, umbral_alto: float | None) -> Sensor
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
`EstadoSensor` y `CultivoConRangos` usan los mismos nombres de campo que el JSON de la API. En `historico`, una fecha sin zona horaria se entiende como UTC. Solo el agricultor dueño puede crear, mover, marcar alertas o dar órdenes; el técnico solo lee.

## Datos de ejemplo (`db/seed.py`)
- 2 usuarios: un agricultor y un técnico (contraseñas de prueba en `.env.example`, guardadas con hash).
- 3 parcelas, como en el simulador: «Invernadero tomates» (`indoor`), «Aguacates» y «Mangos» (`outdoor`).
- 1 nodo por parcela con 4 sensores (uno por magnitud). Los ids salen como los que ya usa el simulador: parcela 1 → sensores 1-4, parcela 2 → 5-8, parcela 3 → 9-12.
- Cultivos: tomate, aguacate, mango y chirimoya. **Los rangos óptimos se rellenan cuando tengamos fuentes fiables** (profesorado de agraria, FAO, La Palma). Hasta entonces se marcan con `source = "PENDIENTE"` y la interfaz lo indica.

## Pendiente de decidir en el grupo
1. ¿Basta con el reparto «agricultor actúa, técnico solo mira», o hace falta un administrador?
2. Cultivo por nodo (propuesto) o por zonas dibujadas en el plano (más trabajo para B).
3. ¿Quién consigue las fuentes de los rangos óptimos y para cuándo?
