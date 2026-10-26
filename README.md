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
La interfaz del panel está en `agrotechEFA2026/pages/dashboard.py`; sus tarjetas
reutilizables y la paleta de colores están en `agrotechEFA2026/components/`.
Los valores actuales son datos ficticios para probar la interfaz.
