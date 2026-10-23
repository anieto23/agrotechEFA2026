<!-- reflex managed begin (do not edit inside this block; add custom content outside the markers) -->
# Agents

This project uses the **Reflex agent skills** — up-to-date knowledge for building full-stack Python web apps with [Reflex](https://reflex.dev). Install them first, then use them as described below.

## Installing the Skills

Before working on this project, make sure the Reflex skills are available to you.

### Claude Code

If the skills are not already available, install them yourself by running these shell commands:

```bash
claude plugin marketplace add reflex-dev/agent-skills
claude plugin install reflex@reflex-agent-skills
```

Newly installed plugins load on the next session. After installing, tell the user to restart the session so the skills auto-load; until then, read the skill files directly from `~/.claude/plugins/` when you need them.

### Other agents (Cursor, OpenCode, Codex, Pi)

```
npx skills add reflex-dev/agent-skills
```

Or clone https://github.com/reflex-dev/agent-skills and copy the `skills/` folders into your agent's skill directory (see the repo README for paths).

### Verifying

Before writing or editing any Reflex code, confirm these three skills are available: `reflex-docs`, `setup-python-env`, and `reflex-process-management`. If they are not, STOP and run the install step above — do not proceed without them.

## Using the Skills

### Reflex documentation

For anything about Reflex APIs — components, state management, events, styling, database, routing, authentication — use the **reflex-docs** skill rather than relying on memory. It carries current, version-accurate docs.

### Initializing a new Reflex project

When starting a new Reflex project or setting up a development environment, you **must** follow the **setup-python-env** skill before doing anything else.

Do not skip any steps. Do not assume a virtual environment or Reflex is already available — always verify first by following the skill's instructions in order.

After the environment is ready and Reflex is installed, run:

```bash
reflex init
```

Then proceed with the user's request.

### Managing a Reflex process

When you need to compile, run, reload, or debug a Reflex application, follow the **reflex-process-management** skill for the correct sequence and error investigation steps.
<!-- reflex managed end -->

# Instrucciones del equipo Agrotech (para cualquier IA)

## Qué es esto
Proyecto del **II Reto Agrotech Startup 2026** (EFA El Soto, Motril). Web app **Python + Reflex** que monitoriza en tiempo real los sensores de una parcela. Equipo de 4 personas (A, B, C, D) que usan IA para casi todo. Entrega **8-dic-2026**, final **16-dic-2026**. Objetivo: **ganar**.
Contexto completo: `docs/BASES-RETO.md`, `docs/contrato.md`, `docs/PLAN-EQUIPO.md`.

## Lo primero que haces en cada sesión
1. Pregunta (o lee en el mensaje) **qué persona eres a tu cargo: A, B, C o D**. Si no lo sabes, pregunta; no adivines.
2. `git pull` y `git status`. Lee `docs/contrato.md` si ha cambiado.
3. Trabaja en rama `feat/<persona>-<tema>`. **Nunca en `main`.**
4. Antes de escribir código de Reflex, usa la skill `reflex-docs` (ver el bloque de arriba). No uses la memoria para APIs de Reflex: la versión es 0.10 y cambia.

## Reparto: solo editas TUS carpetas
| Persona | Carpetas propias |
|---|---|
| A – Backend y datos | `db/`, `api/`, `migrations/` |
| B – Panel y gráficos | `pages/dashboard.py`, `pages/historico.py`, `components/charts.py`, `components/sensor_card.py`, `state/dashboard_state.py` |
| C – Gestión y alertas | `pages/login.py`, `pages/parcelas.py`, `pages/sensores.py`, `pages/alertas.py`, `components/layout.py`, `components/forms.py`, `state/gestion_state.py`, `state/auth_state.py`, `services/alertas.py` |
| D – Sensores e inteligencia | `scripts/`, `firmware/`, `services/riego.py`, `services/telegram.py`, `services/export.py`, `Dockerfile`, `docs/hardware.md` |

- **Carpeta ajena = no se toca.** Si necesitas un cambio ahí, dilo a la persona y deja escrito qué función o campo necesitas. Si es urgente, propón el cambio como PR pequeño a esa persona.
- **Archivos compartidos** (`agrotechEFA2026.py`, `rxconfig.py`, `pyproject.toml`, `docs/contrato.md`): solo con PR pequeño, avisando a todos. Los gestiona A.
- Nunca cambies el **contrato** (tablas, endpoints, JSON) por tu cuenta. Se propone en `docs/contrato.md` y los 4 lo aprueban.

## Cómo te comportas con la persona
- Habla **español**, claro y corto. Son estudiantes de FP: explica qué hiciste en 2-3 líneas, sin jerga innecesaria.
- Haz tú el trabajo (código, tests, docs). La persona solo prueba, revisa y confirma. **No le pases tareas que puedes hacer tú**; propón algo ya hecho y pídele un "sí/no".
- Si falta información que solo la persona tiene (hardware, claves, decisiones), pregunta **una vez, concreto**, y sigue con lo que puedas.
- **No inventes**: ni datos, ni resultados de tests, ni funciones de la API de Reflex. Si no lo has ejecutado, di que no lo has comprobado.
- Si algo falla, di qué falló con el error real. No lo escondas ni lo marques como terminado.

## Calidad que puntúa en el reto (baremo): funcionalidad 40 · código 15 · interfaz 15 · docs 10 · git 10 · extras 10
- **Código:** claro, con nombres en español o inglés pero coherentes, y un comentario donde la lógica no sea evidente. Sin código muerto ni copiado. Funciones cortas.
- **Tests:** toda lógica con ramas (alertas, riego, validaciones, API) lleva test con `pytest`. Ejecútalo antes de dar nada por hecho.
- **Interfaz:** debe verse bien en móvil (375 px), tablet y ordenador. Estados vacíos, de carga y de error. No indicar nada solo con color.
- **Documentación:** cada módulo nuevo actualiza su sección del `README.md` y `docs/arquitectura.md` (máx. 2 páginas en total, sin relleno).
- **Git:** commits pequeños y descriptivos en español ("Añade umbral mínimo a los sensores"), un tema por rama, PR con descripción de qué cambia y cómo probarlo. **Otra persona aprueba el PR.**

## Seguridad y límites (innegociables)
- **Nunca** subas secretos: tokens, contraseñas, claves de API. Van en `.env` (ya en `.gitignore`); en el repo solo `.env.example`.
- Contraseñas con hash, nunca en texto plano. Valida todo lo que llegue a la API (rango de valores, tipos, pertenencia del sensor).
- **Licencia GPL v3 o posterior.** No metas código ni dependencias con licencia incompatible; no pegues código de otros sin comprobar su licencia.
- Todo es **software libre**. No añadas servicios de pago ni cuentas personales sin que la persona lo apruebe.
- **No hagas push a `main`, no fuerces (`--force`), no borres ramas de otros, no reescribas historia.**
- **No inscribas al equipo ni envíes formularios o mensajes externos** sin que la persona lo apruebe en esa conversación.
- No abras ni modifiques archivos fuera de este repo.

## Dependencias y entorno
- Python 3.12 funciona (el `pyproject.toml` pide ≥3.15, ignóralo hasta que A lo cambie). Reflex 0.10.
- Instalar: `pip install -r requirements.txt` (si no existe, pide a A que lo genere desde `pyproject.toml`). Arrancar: `python -m reflex run` (web :3000, API :8000).
- No instales dependencias nuevas sin añadirlas a `pyproject.toml` y avisar en el PR.
- Si el ordenador va justo de memoria, no dejes `reflex run` abierto sin necesidad.

## Al terminar una tarea, di siempre
1. Qué cambiaste (archivos).
2. Cómo probarlo (comando o pasos).
3. Qué tests pasaron (resultado real).
4. Qué falta o qué riesgo queda.
5. Qué tiene que aprobar la persona o quién del equipo debe revisar el PR.
