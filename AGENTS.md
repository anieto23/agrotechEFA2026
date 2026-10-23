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
Proyecto del **II Reto Agrotech Startup 2026** (EFA El Soto, Motril). Web app **Python + Reflex** que monitoriza en tiempo real los sensores de una parcela. Equipo de 6 personas (A, B, C, D, E, F) que usan IA para casi todo. Entrega **8-dic-2026**, final **16-dic-2026**. Objetivo: **ganar**.
Contexto completo: `docs/BASES-RETO.md`, `docs/contrato.md`, `docs/PLAN-EQUIPO.md`.

## Lo primero que haces en cada sesión
1. Pregunta (o lee en el mensaje) **qué persona eres a tu cargo: A, B, C, D, E o F**. Si no lo sabes, pregunta; no adivines.
2. `git switch main`, `git pull` y `git status`. Lee `docs/contrato.md` si ha cambiado.
3. Trabaja en rama `feat/<persona>-<tema>` creada desde `main` recién actualizada. **Nunca en `main`.** Sigue `docs/GIT-SEGURO.md`.
4. Antes de escribir código de Reflex, usa la skill `reflex-docs` (ver el bloque de arriba). No uses la memoria para APIs de Reflex: la versión es 0.10 y cambia.

## Reparto: solo editas TUS carpetas
| Persona | Carpetas propias |
|---|---|
| A – Backend y datos | `db/`, `api/`, `migrations/` |
| B – Panel y gráficos | `pages/dashboard.py`, `pages/historico.py`, `components/charts.py`, `components/sensor_card.py`, `state/dashboard_state.py` |
| C – Gestión y alertas | `pages/login.py`, `pages/parcelas.py`, `pages/sensores.py`, `pages/alertas.py`, `components/layout.py`, `components/forms.py`, `state/gestion_state.py`, `state/auth_state.py`, `services/alertas.py` |
| D – Sensores (hardware y simulador) | `scripts/`, `firmware/`, `docs/hardware.md` |
| E – Inteligencia y avisos | `services/riego.py`, `services/telegram.py`, `services/export.py` |
| F – Calidad, despliegue y entrega | `.github/` (CI, `CODEOWNERS`), `Dockerfile`, `README.md` (coordina las secciones), `docs/arquitectura.md`, `docs/presentacion/` |

Las rutas de código cuelgan de `agrotechEFA2026/`. Quién aprueba cada carpeta está en `.github/CODEOWNERS`.

- **Carpeta ajena = no se toca.** Si necesitas un cambio ahí, dilo a la persona y deja escrito qué función o campo necesitas. Si es urgente, propón el cambio como PR pequeño a esa persona.
- **Archivos compartidos** (`agrotechEFA2026.py`, `rxconfig.py`, `pyproject.toml`, `docs/contrato.md`): solo con PR pequeño, avisando a todos. Los gestiona A.
- Nunca cambies el **contrato** (tablas, endpoints, JSON) por tu cuenta. Se propone en `docs/contrato.md` y los 6 lo aprueban.

## Git sin pisar a nadie (obligatorio)
- **Prohibido:** `git push --force` (ni `--force-with-lease`), `git reset --hard` sobre trabajo subido, `git rebase` de ramas ya subidas, borrar ramas ajenas, subir a `main`.
- **Si `git push` es rechazado** ("rejected", "fetch first"): no fuerces. Haz `git pull` en tu rama y vuelve a subir.
- **Conflictos:** nunca elijas "lo mío" o "lo suyo" a ciegas. Si el conflicto está en una carpeta ajena o en un archivo compartido, **para y avisa a la persona**; enséñale las dos versiones y que decida. Tras resolver, arranca la app y pasa los tests antes de subir.
- **No borres ni muevas archivos** que no sean de tu carpeta, aunque parezcan sin usar.
- Antes de pedir el PR: `git fetch` y `git merge origin/main` en tu rama, prueba que todo arranca y sube. Si el PR toca algo fuera de tus carpetas, dilo en la descripción.
- `git add` solo de los archivos que has cambiado a propósito (nada de `git add .` sin mirar `git status`).

## Procedimientos de git: la persona habla normal, tú haces los comandos
La persona no tiene por qué saber git. Cuando diga algo de lo de abajo, sigue el procedimiento **entero y en orden**, ejecutando tú los comandos. Explicación para humanos: `docs/GIT-SEGURO.md`.

### «Empiezo» / «voy a hacer X» / al abrir la sesión
1. Si no sabes su letra (A–F), pregúntala. Comprueba `git config user.name` y `user.email`; si faltan, pídeselos y configúralos.
2. `git status`. Si hay cambios sin guardar de otra tarea, avisa antes de cambiar de rama (ofrece hacer commit en su rama; no los descartes).
3. `git switch main` → `git pull` → `git switch -c feat/<letra>-<tema-corto>` (sin tildes ni espacios, p. ej. `feat/b-grafico-humedad`). Si la rama ya existe: `git switch` a ella y `git merge main`.

### «Haz el commit» / «súbelo» / «ya he terminado»
1. **Rama:** `git branch --show-current`. Si es `main`, crea su rama ahora (`git switch -c feat/<letra>-<tema>`; los cambios se van con ella). Nunca hagas commit en `main`.
2. **Revisa qué ha cambiado:** `git status` y `git diff`. Clasifica cada archivo:
   - **Suyo** (sus carpetas, sus `tests/`, su `docs/equipo/<letra>-*/`) → se sube.
   - **Ajeno o compartido** → NO lo añadas. Díselo: qué archivo, de quién es y qué cambio había. Que decida (dejarlo fuera, o PR aparte avisando al dueño).
   - **Sospechoso** (`.env`, claves, tokens, contraseñas, bases de datos `.db`, datos generados, archivos de más de 5 MB, `__pycache__`, `.web/`) → NO lo añadas y avisa.
3. **Secretos:** busca en lo que vas a subir `token`, `password`, `api_key`, `secret` y cosas como `123456789:ABC…`. Si hay alguno con valor real, para.
4. **Prueba:** si hay tests, `python -m pytest` y enseña el resultado real. Si fallan, díselo y pregunta si sube igualmente (y lo pones en la descripción del PR).
5. **Commit:** `git add <archivos suyos>` uno a uno o por carpeta, y `git commit -m "<Verbo> <qué>"` en español («Añade…», «Corrige…», «Quita…»). Si hay dos temas distintos, dos commits.
6. **Trae lo de los demás:** `git fetch` y `git merge origin/main`. Si hay conflicto, sigue «Conflicto» abajo.
7. **Sube:** `git push -u origin <rama>`. Si dice *rejected* / *fetch first*: `git pull` (merge, no rebase) y vuelve a subir. Nunca `--force`.
8. **PR:** si hay `gh` y sesión iniciada, `gh pr create --base main --title "..." --body "..."`, y si sabes el usuario de su compañero de rotación (A→B→C→D→E→F→A), `--reviewer <usuario>`. Si no hay `gh`, dale a la persona el enlace que imprimió `git push` (`.../pull/new/<rama>`) y **el título y la descripción ya escritos para pegar**. La descripción lleva: qué cambia, cómo probarlo, resultado de los tests y si toca algo fuera de sus carpetas. El PR lo abre **la persona con su cuenta**.
9. Termina con el resumen de «Al terminar una tarea» (abajo) y recuérdale a quién pedir la revisión.

### «Ya me lo han aprobado» / «está unido»
`git switch main` → `git pull` → `git branch -d <rama>` (con `-d`, nunca `-D`: si dice que no está unida, no la borres y avisa).

### «Revisa el PR de X»
`git fetch` → `git switch <su-rama>` → arranca la app y los tests → di si hace lo que promete, si solo toca sus carpetas y si hay secretos. Aprobar lo hace la persona en GitHub; tú le das tu opinión. Al acabar, vuelve a su rama de trabajo.

### Conflicto
1. `git status` para ver los archivos en conflicto. En cada uno, enséñale las dos versiones en cristiano (qué hacía cada una).
2. Si el archivo es **suyo**: propón una versión que conserve lo correcto de las dos y pide su sí.
3. Si es **ajeno o compartido**: no lo resuelvas. `git merge --abort` y dile a quién tiene que avisar.
4. Tras resolver: `git add <archivo>`, `git commit`, tests y push.

### Errores típicos
| Mensaje | Qué hacer |
|---|---|
| `Authentication failed` / ventana de inicio de sesión | La persona inicia sesión en GitHub en esa ventana (no le pidas la contraseña ni el token) |
| `Permission denied` / `403` | No tiene acceso: que anieto23 la invite (Settings → Collaborators) |
| `protected branch` / `GH006` | Intentaba subir a `main`. Pasa los commits a una rama (`git switch -c feat/...`) y sube esa |
| `Your local changes would be overwritten` | Haz commit en su rama primero (o `git stash` y luego `git stash pop`). Nunca descartes cambios sin su sí |
| `You are in 'detached HEAD'` | `git switch -c feat/<letra>-<tema>` para no perder nada |
| `merge in progress` / `MERGING` | Termina el conflicto (arriba) o `git merge --abort` |
| Cualquier otra cosa | Enséñale el error real y explica qué significa antes de probar nada destructivo |

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
