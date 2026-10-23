# Guion de A – Backend y datos

**Eres la base de todos:** B, C y D esperan tus tablas y tu API. Por eso tu semana 1 es la más importante. Haz primero lo que desbloquea a los demás.
**Tus carpetas:** `db/`, `api/`, `migrations/` + gestionas los archivos compartidos (`agrotechEFA2026.py`, `rxconfig.py`, `pyproject.toml`).
Lee antes `docs/GUION-COMUN.md` y `AGENTS.md`.

## Semana 1 (→30 oct) – desbloquear al equipo
**A1. Contrato.** Pega a Claude:
> Soy A. Redacta `docs/contrato.md` con: (1) tablas `users, parcels, sensors, sensor_data, alerts` con campos, tipos y relaciones (usa SQLModel/`rx.Model`; sensores con `api_key`, `umbral_min`, `umbral_max`, `activo`; parcelas con `cultivo`, `lat`, `lon`); (2) endpoints con ejemplos JSON; (3) las funciones de acceso a datos que `db/` ofrecerá a B y C (nombres y firmas). Basado en las bases del reto en `docs/BASES-RETO.md`.

**Tú:** lees el contrato, lo discutes 15 min con B, C y D, y lo apruebas por PR. Es la decisión más importante del proyecto.

**A2. Modelos y datos de ejemplo.** > Implementa los modelos en `db/models.py`, la sesión en `db/session.py` y `db/seed.py` con 2 usuarios demo (agricultor y técnico, contraseña con hash), 2 parcelas y 4 sensores. Añade un test.
**A3. Dependencias.** > Genera `requirements.txt` desde `pyproject.toml`, baja el `requires-python` a lo que funcione de verdad (3.12) y deja instalado sqlmodel, pytest y alembic.

## Semana 2 (→6 nov) – que entren los datos
**A4. Ingestión.** > Crea `POST /api/sensors/{sensor_id}/data` con la cabecera `X-API-Key`: valida clave, rango por tipo, formato de fecha ISO; guarda en `sensor_data` y llama a `services.alertas.evaluar()` si existe. Devuelve errores claros (401, 404, 422). Tests de cada error.
**A5. Lectura.** > Crea `GET /api/parcels`, `GET /api/parcels/{id}/sensors`, `GET /api/sensors/{id}/data?from=&to=&limit=` con paginación y `GET /api/dashboard` (última lectura por sensor y estado).
Verás los datos con el simulador de D; pide a D que te avise cuando lo tenga.

## Semana 3 (→13 nov) – acceso y seguridad
**A6. Login.** > Crea `POST /api/auth/login` (token) y la comprobación de rol en los endpoints: el técnico solo lee. Contraseñas con hash. Coordina con C, que hace la pantalla.
**A7. Aislamiento.** Cada usuario solo ve **sus** parcelas. > Añade el filtro por propietario y un test con dos usuarios.

## Semana 4 (→20 nov) – tiempo real
**A8. Actualización en vivo.** > Implementa el refresco en tiempo real del panel: primero con sondeo cada 5 s desde el State de B; si da tiempo, WebSocket `WS /ws/parcels/{id}`. Mide que 50 lecturas por segundo no la rompen.

## Semana 5 (→27 nov) – robustez
- Migraciones con alembic, índices por (`sensor_id`, `timestamp`), purga/agregado de datos viejos.
- Documentar la API (ejemplos de payload en el README) y escribir tu sección de `docs/arquitectura.md`.

## Semana 6 (→4 dic)
Congelar la API. Revisión cruzada final y preparar la base de datos de ejemplo para la demo (copia limpia con 14 días de histórico).

## Qué entregas a los demás
| Para | Qué | Cuándo |
|---|---|---|
| B y C | `docs/contrato.md` aprobado | 28 oct |
| B y C | funciones de `db/` con datos de ejemplo | 30 oct |
| D | endpoint de ingestión | 6 nov |
| C | login y roles | 13 nov |

## Riesgos
- Cambiar el esquema una vez que otros programan sobre él → después de aprobar el contrato, cualquier cambio va por PR y con aviso.
- Lecturas falsas o fuera de rango → validar todo en la entrada.
