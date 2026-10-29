# agrotechEFA2026
Proyecto de EFA El Soto para el Reto Agrotech 2026

App para dibujar la parcela a escala, colocar sus sensores, comparar cada lectura con
los valores óptimos del cultivo y actuar desde el móvil. Idea completa y fases en
[`docs/IDEA-PROYECTO.md`](docs/IDEA-PROYECTO.md). Cómo ha evolucionado el trabajo:
[`docs/EVOLUCION.md`](docs/EVOLUCION.md).

## Instalación

Requiere Python 3.11 o superior.

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows (en Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python -m pytest                  # comprobar que todo funciona
python -m reflex run              # web en http://localhost:3000
```

## Base de datos

Tablas, API y funciones descritas en [`docs/contrato.md`](docs/contrato.md); el código está en
`agrotechEFA2026/db/`. Por defecto usa SQLite (`agrotech.db`); para MySQL/MariaDB, define
`AGROTECH_DB_URL` (ver `.env.example`).

Datos de ejemplo (2 usuarios, las 3 parcelas del simulador y 12 sensores):

```bash
python -m agrotechEFA2026.db.seed
```

Muestra las contraseñas de `agricultor` y `tecnico` si no están en `AGROTECH_PASS_FARMER` /
`AGROTECH_PASS_TECHNICIAN`, y guarda las claves de los aparatos en `claves_demo.json` para
el simulador (`--claves claves_demo.json`).

Cada parcela se divide en **sectores** (zonas con su cultivo y como mucho un sensor de cada
tipo). Si se dibuja a mano, guarda también su contorno.

### Migraciones (cambiar las tablas sin perder datos)

Los cambios de tablas se guardan como «recetas» en `migrations/versions/` (Alembic). La app
aplica las que falten al arrancar; también se puede hacer a mano:

```bash
python -m agrotechEFA2026.db.migrar                          # poner agrotech.db al día
python -m agrotechEFA2026.db.migrar nueva "añade X a Y"      # tras cambiar db/models.py
python -m agrotechEFA2026.db.migrar unir                     # si dos personas crearon una a la vez
```

Quien cambie `db/models.py` sube también su migración (los tests fallan si falta).

## API REST

La API (FastAPI) va dentro de la app de Reflex, en el puerto 8000. Con la app en marcha, la
documentación interactiva está en http://127.0.0.1:8000/docs.

| Método y ruta | Qué hace |
|---|---|
| `POST /api/sensors/{sensor_id}/data` | Guarda una lectura (cabecera `X-API-Key` del aparato) y crea la alerta si sale del rango |

Ejemplo:

```bash
curl -X POST http://127.0.0.1:8000/api/sensors/3/data -H "X-API-Key: <clave>" -H "Content-Type: application/json" -d '{"value": 31.5, "type": "soil_moisture", "unit": "%"}'
```

Respuesta `201`: `{"id": 1, "sensor_id": 3, "timestamp": "...Z", "value": 31.5, "alert": {"type": "LOW", "message": "..."}}`.
Errores: `401` clave incorrecta, `404` sensor inexistente, `422` datos no válidos; siempre `{"detail": "<motivo>"}`.

Probar con el simulador (solo la parte de servidor, sin la web):

```bash
python -m reflex run --backend-only
python scripts/gen_sample_data.py --historico 1 --url http://127.0.0.1:8000 --claves claves_demo.json
```

En Windows usa `127.0.0.1` y no `localhost`: con `localhost` cada envío tarda unos 2 segundos más.

## Panel de control

La aplicación registra la página principal desde `agrotechEFA2026/agrotechEFA2026.py`.
El panel en `agrotechEFA2026/pages/dashboard.py` permite probar la navegación entre
parcelas, sectores y mediciones. La maqueta permite crear parcelas indicando su superficie
y dibujando el contorno con vértices en una cuadrícula. Se pueden deshacer y borrar puntos,
y cerrar el contorno; no se admiten lados cruzados. También permite eliminar parcelas
con confirmación, dibujar sectores poligonales sin solapes, asignar cultivos y añadir
sensores. Al eliminar una parcela también se eliminan sus sectores de muestra. Las medias
ignoran sectores que todavía no tienen lectura para esa magnitud.

Esta parte aún usa datos de ejemplo en memoria: los cambios no se guardan al cerrar la
sesión. La base de datos ya guarda formas, contornos dibujados y sectores (ver
[`docs/contrato.md`](docs/contrato.md)); falta conectar la maqueta a esas funciones. El contorno dibujado
se guarda como proporciones de la cuadrícula, no representa coordenadas reales ni está a
escala. En la maqueta se puede reemplazar la distribución de sectores dibujando sus
contornos: se permiten huecos, se rechazan solapes y se valida que queden dentro de la
parcela. La distribución dibujada es temporal; el modelo persistente todavía representa
los sectores con límites rectangulares.
