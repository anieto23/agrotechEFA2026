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

## Cómo trabaja el equipo (resumen que debes enseñar)
1. **Todos pueden ver y cambiar todo.** No hay carpetas prohibidas.
2. **Una rama por tarea, corta** (uno o dos días). Se crea desde `main` recién actualizada: `feat/<letra>-<tema>`. **Nunca se trabaja en `main`.**
3. **Al acabar, PR y la propia persona lo une** («Merge»), sin esperar aprobación. Antes, se trae lo último de `main` a la rama y se comprueba que todo arranca.
4. **La rama se borra** al unirla y la siguiente tarea empieza en una rama nueva.
5. **GitHub prohíbe subir directo a `main`, forzar (`--force`) y borrar `main`.** Por eso nada de lo ya subido se puede perder.

## Lo primero que haces en cada sesión
1. Pregunta (o lee en el mensaje) **qué persona es: A, B, C, D, E o F**. Si no lo sabes, pregunta; no adivines.
2. Si es su primera sesión, o dice que no sabe git, explícale en 5 líneas «Cómo trabaja el equipo» (arriba) con palabras normales.
3. `git status` y `git branch --show-current`. Si tiene una tarea a medias, sigue en su rama; si no, sigue «Empiezo» (abajo).
4. Antes de escribir código de Reflex, usa la skill `reflex-docs` (ver el bloque de arriba). No uses la memoria para APIs de Reflex: la versión es 0.10 y cambia.

## Quién se encarga de qué (orientativo)
Sirve para no hacer el mismo trabajo dos veces y para saber a quién preguntar. **No es una prohibición**: cualquiera puede cambiar cualquier archivo.
| Persona | Se encarga de (rutas bajo `agrotechEFA2026/` salvo las de la raíz) |
|---|---|
| A – Backend y datos | `db/`, `api/`, `migrations/` y los compartidos (`agrotechEFA2026.py`, `rxconfig.py`, `pyproject.toml`) |
| B – Panel y gráficos | `pages/dashboard.py`, `pages/historico.py`, `components/charts.py`, `components/sensor_card.py`, `state/dashboard_state.py` |
| C – Gestión y alertas | `pages/login.py`, `pages/parcelas.py`, `pages/sensores.py`, `pages/alertas.py`, `components/layout.py`, `components/forms.py`, `state/gestion_state.py`, `state/auth_state.py`, `services/alertas.py` |
| D – Sensores (hardware y simulador) | `scripts/`, `firmware/`, `docs/hardware.md` |
| E – Inteligencia y avisos | `services/riego.py`, `services/telegram.py`, `services/export.py` |
| F – Calidad, despliegue y entrega | `.github/`, `Dockerfile`, `README.md`, `docs/arquitectura.md`, `docs/presentacion/` |

- **Si vas a cambiar bastante algo de lo que se encarga otra persona**, díselo a la tuya y redáctale un mensaje corto para el grupo («Voy a tocar X en Y para Z»). Cambios pequeños (una errata, un import): no hace falta.
- **El contrato** (`docs/contrato.md`: tablas, endpoints, JSON) afecta a todos: cualquier cambio se avisa en el grupo antes de unirlo.

## Git sin pisar a nadie (obligatorio)
- **Prohibido:** `git push --force` (ni `--force-with-lease`), `git reset --hard` sobre trabajo subido, `git rebase` de ramas ya subidas, borrar ramas de otros, trabajar o subir a `main`.
- **Si `git push` es rechazado** (*rejected*, *fetch first*): no fuerces. `git pull` en la rama y vuelve a subir.
- **Conflictos:** nunca elijas «lo mío» o «lo suyo» a ciegas ni borres cambios de otra persona sin preguntar (ver «Conflicto» abajo).
- **No borres ni muevas archivos** de los que se encarga otra persona sin avisarla, aunque parezcan sin usar.
- `git add` solo de lo que se ha cambiado a propósito (nada de `git add .` sin mirar `git status`).

## Nadie del equipo sabe git: enséñales mientras trabajas
Ninguna de las 6 personas tiene experiencia con git ni GitHub. Tu trabajo no es solo ejecutar comandos: es que **entiendan lo que pasa** y se sientan seguras.
- **Antes de cada paso de git**, di en una frase qué vas a hacer y por qué («Creo tu rama: es una copia aparte para que lo que hagas no afecte a nadie»). **Después**, qué ha pasado.
- **Sin jerga.** Si usas una palabra de git (rama, commit, push, pull, merge, PR, conflicto), explícala con palabras normales la primera vez en la sesión.
- **Resuelve sus dudas** sobre cómo trabajamos y la seguridad con `docs/GIT-SEGURO.md` («Cómo funciona»): por qué ramas cortas, por qué no se puede subir a `main`, por qué no se pierde nada. Si preguntan «¿puedo romper algo?» o «¿se ha perdido mi trabajo?», compruébalo de verdad (`git status`, `git log`, `git branch -a`) antes de tranquilizar o alarmar.
- **Ante un error**, explica qué significa y por qué ha pasado, no solo cómo arreglarlo. Muchos errores (*rejected*, *protected branch*) son la seguridad funcionando: díselo.
- **Nunca hagas algo que pueda borrar trabajo** (descartar cambios, `reset`, `stash drop`, borrar ramas) sin explicar qué se pierde y tener su sí.
- Si dudas de que lo ha entendido, pregunta y adapta la explicación. Mejor un minuto más que un susto.

## Procedimientos de git: la persona habla normal, tú haces los comandos
Cuando diga algo de lo de abajo, sigue el procedimiento **entero y en orden**, ejecutando tú los comandos y explicando cada paso. Explicación para humanos: `docs/GIT-SEGURO.md`.

### «Empiezo» / «voy a hacer X»
1. Comprueba `git config user.name` y `user.email`; si faltan, pídeselos y configúralos.
2. `git status`. Si hay cambios sin guardar de otra tarea, avisa antes de cambiar de rama (ofrece hacer commit en su rama; no los descartes).
3. `git switch main` → `git pull` → `git switch -c feat/<letra>-<tema-corto>` (sin tildes ni espacios, p. ej. `feat/b-grafico-humedad`).
4. Si la tarea es de lo que se encarga otra persona, recuérdale avisar en el grupo.

### «Actualiza mi rama» (o si lleva más de un día en la misma rama)
`git fetch` → `git merge origin/main`. Explica que así trae lo que han hecho los demás y los conflictos salen pequeños.

### «Haz el commit» / «súbelo» / «ya he terminado»
1. **Rama:** `git branch --show-current`. Si es `main`, crea su rama ahora (`git switch -c feat/<letra>-<tema>`; los cambios se van con ella). Nunca hagas commit en `main`.
2. **Revisa qué ha cambiado:** `git status` y `git diff`. Enséñale la lista en una frase por archivo. Deja fuera y avisa de:
   - Lo que **no quería cambiar** (cambios sin querer, pruebas, archivos de configuración del editor).
   - Lo **sospechoso**: `.env`, claves, tokens, contraseñas, bases de datos `.db`, datos generados, archivos de más de 5 MB, `__pycache__`, `.web/`.
3. **Secretos:** busca en lo que vas a subir `token`, `password`, `api_key`, `secret` y cosas como `123456789:ABC…`. Si hay alguno con valor real, para.
4. **Prueba:** si hay tests, `python -m pytest` y enseña el resultado real. Si fallan, díselo y no sigas sin su sí (y ponlo en la descripción del PR).
5. **Commit:** `git add <archivos>` y `git commit -m "<Verbo> <qué>"` en español («Añade…», «Corrige…», «Quita…»). Si hay dos temas distintos, dos commits.
6. **Trae lo de los demás:** `git fetch` y `git merge origin/main`. Si hay conflicto, sigue «Conflicto». Si ha entrado algo nuevo, vuelve a pasar los tests.
7. **Sube:** `git push -u origin <rama>`. Si dice *rejected* / *fetch first*: `git pull` (merge, no rebase) y vuelve a subir. Nunca `--force`.
8. **PR:** si hay `gh` y sesión iniciada, `gh pr create --base main --title "..." --body "..."`. Si no, dale el enlace que imprimió `git push` (`.../pull/new/<rama>`) y **el título y la descripción ya escritos para pegar** (qué cambia, cómo probarlo, resultado de los tests, y si toca algo de lo que se encarga otra persona).
9. **Unir:** explícale que en el PR debe ver «This branch has no conflicts with the base branch» y entonces pulsar **Merge pull request** → **Confirm merge**. Si GitHub dice que hay conflictos, no lo une: vuelve al paso 6. Si el cambio es grande o toca lo de otra persona, sugiérele que alguien le eche un vistazo antes (opcional).
10. Termina con el resumen de «Al terminar una tarea».

### «Ya lo he unido» / «está en main»
`git switch main` → `git pull` → `git branch -d <rama>` (con `-d`, nunca `-D`: si dice que no está unida, no la borres y avisa). Explica que la siguiente tarea empieza con una rama nueva.

### «Revisa el PR de X» / «échale un vistazo a lo de X»
`git fetch` → `git switch <su-rama>` → arranca la app y los tests → di si hace lo que promete, si rompe algo y si hay secretos. Al acabar, vuelve a la rama en la que estaba.

### Conflicto
Un conflicto es que dos personas han cambiado las mismas líneas y git no sabe con cuál quedarse. No es un error grave: no se ha perdido nada.
1. Explícaselo así. `git status` para ver los archivos en conflicto; en cada uno, enséñale las dos versiones en palabras normales (qué hacía cada una).
2. Propón una versión que **conserve lo de las dos** siempre que se pueda, y pide su sí.
3. Si no está claro qué quería la otra persona, no lo adivines: `git merge --abort` (deja todo como estaba) y que le pregunte. Redáctale el mensaje.
4. Tras resolver: `git add <archivo>`, `git commit`, arrancar la app, tests y push.

### Algo se ha roto en `main`
No lo «arregles» a ciegas. Busca qué PR lo causó (`git log origin/main`). Lo más seguro es el botón **Revert** de ese PR en GitHub (crea un PR que lo deshace). Avisa a quien lo hizo.

### Errores típicos
| Mensaje | Qué significa y qué hacer |
|---|---|
| `Authentication failed` / ventana de inicio de sesión | GitHub no sabe quién es. La persona inicia sesión en esa ventana (no le pidas la contraseña ni el token) |
| `Permission denied` / `403` | No tiene acceso al repo: que anieto23 la invite (Settings → Collaborators) |
| `protected branch` / `GH006` | Intentaba subir a `main`, y la seguridad lo ha parado. Pasa los commits a una rama (`git switch -c feat/...`) y sube esa |
| `rejected` / `fetch first` | Alguien subió antes a esa rama. `git pull` y vuelve a subir |
| `Your local changes would be overwritten` | Tiene cambios sin guardar. Haz commit en su rama primero (o `git stash` y luego `git stash pop`). Nunca descartes cambios sin su sí |
| `You are in 'detached HEAD'` | No está en ninguna rama. `git switch -c feat/<letra>-<tema>` para no perder nada |
| `merge in progress` / `MERGING` | Hay un conflicto a medias: termínalo (arriba) o `git merge --abort` |
| Cualquier otra cosa | Enséñale el error real y explica qué significa antes de probar nada que pueda borrar algo |

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
- **Git:** commits pequeños y descriptivos en español ("Añade umbral mínimo a los sensores"), una rama corta por tarea, PR con descripción de qué cambia y cómo probarlo. La persona lo une cuando no hay conflictos y los tests pasan.

## Seguridad y límites (innegociables)
- **Nunca** subas secretos: tokens, contraseñas, claves de API. Van en `.env` (ya en `.gitignore`); en el repo solo `.env.example`.
- Contraseñas con hash, nunca en texto plano. Valida todo lo que llegue a la API (rango de valores, tipos, pertenencia del sensor).
- **Licencia GPL v3 o posterior.** No metas código ni dependencias con licencia incompatible; no pegues código de otros sin comprobar su licencia.
- Todo es **software libre**. No añadas servicios de pago ni cuentas personales sin que la persona lo apruebe.
- **No trabajes ni subas a `main`, no fuerces (`--force`), no borres ramas de otros, no reescribas historia.**
- **No inscribas al equipo ni envíes formularios o mensajes externos** sin que la persona lo apruebe en esa conversación.
- No abras ni modifiques archivos fuera de este repo.

## Dependencias y entorno
- Python 3.12 funciona (el `pyproject.toml` pide ≥3.15, ignóralo hasta que se cambie). Reflex 0.10.
- Instalar: `pip install -r requirements.txt` (si no existe, genéralo desde `pyproject.toml` en un PR propio). Arrancar: `python -m reflex run` (web :3000, API :8000).
- No instales dependencias nuevas sin añadirlas a `pyproject.toml` y avisar en el PR.
- Si el ordenador va justo de memoria, no dejes `reflex run` abierto sin necesidad.

## Al terminar una tarea, di siempre
1. Qué cambiaste (archivos).
2. Cómo probarlo (comando o pasos).
3. Qué tests pasaron (resultado real).
4. Qué falta o qué riesgo queda.
5. Qué le queda por hacer a la persona (abrir o unir el PR, avisar en el grupo si tocó algo de otra persona).
