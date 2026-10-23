# Cómo trabajamos con Git sin pisarnos

Guía para los 6. Nadie tiene que saber Git: **vuestra IA lo hace y os lo explica**. Aquí está lo que hace, para que lo entendáis y sepáis qué pedirle.

## La forma de trabajar en 5 frases

1. **Todos podemos ver y cambiar todo.** No hay carpetas prohibidas; el reparto de `docs/PLAN-EQUIPO.md` solo dice quién se encarga de qué.
2. **Cada tarea se hace en una rama nueva y corta** (uno o dos días), que empieza siendo una copia de `main` con lo último de todos.
3. **Al acabar, abres un PR y lo unes tú** (botón *Merge*), sin esperar a nadie, si GitHub dice que no hay conflictos.
4. **La rama se borra** al unirla y la siguiente tarea empieza con otra rama nueva.
5. **GitHub no deja subir directo a `main`, ni forzar, ni borrar `main`.** Por eso nada de lo subido se puede perder.

---

## Cómo funciona (en 2 minutos)

**Palabras que vais a oír:**
| Palabra | Qué es |
|---|---|
| **`main`** | La versión buena del proyecto, la que se entrega |
| **Rama** | Una copia aparte de `main` para hacer una tarea. Lo que haces en ella no afecta a nadie |
| **Commit** | Guardar un punto de tu trabajo con una frase que dice qué has hecho |
| **Push** (subir) | Mandar tus commits a GitHub. Hasta entonces solo están en tu ordenador |
| **Pull** (traer) | Bajar lo que han subido los demás |
| **PR** (*pull request*) | Pedir en GitHub que tu rama entre en `main`. Muestra qué cambia y si choca con algo |
| **Merge** (unir) | Meter los cambios de tu rama en `main` |
| **Conflicto** | Dos personas han cambiado *las mismas líneas* y Git pregunta con cuál quedarse |

**¿Por qué no nos pisamos si todos tocamos todo?**
- **Git junta los cambios solo.** Si tú cambias un archivo y otra persona cambia otro, o el mismo archivo en otras líneas, Git une las dos cosas sin preguntar y no se pierde nada.
- **Solo pregunta si hay conflicto** (mismas líneas). Entonces tu IA te enseña las dos versiones y os quedáis con lo bueno de las dos. Nunca borra lo del otro sin preguntarte.
- **Las ramas cortas hacen que casi no haya conflictos.** Cada tarea empieza desde el `main` de ese día, que ya trae lo de todos.
- **Si alguien subió antes que tú, Git rechaza tu subida** («rejected») hasta que traes lo suyo. No puede machacarlo.
- **GitHub protege `main`:** nadie puede subir directo (solo por PR), ni forzar una subida (`--force`, lo único que borra trabajo ya subido), ni borrarla.
- **Todo queda en el historial.** Si un PR estropea algo, su botón **Revert** lo deshace.

Resumen: **ramas cortas** + **PR que une cada uno** + **sin `--force`** = todos tocáis todo y nada se pierde.

---

## Primer día (cada persona, una vez)

1. **Acepta la invitación** al repositorio que te llega al correo de GitHub (si no te llega, pídesela a anieto23).
2. **Descarga el proyecto.** En VS Code: *Ctrl+Shift+P* → «Git: Clone» → pega `https://github.com/anieto23/agrotechEFA2026.git` → elige carpeta → *Abrir*. Si ya lo tenías, ábrelo y en la terminal escribe `git pull`.
3. **Abre tu IA en esa carpeta** y pega:
   > Soy la persona **X** del proyecto Agrotech y no sé usar git. Lee `AGENTS.md`, `docs/GIT-SEGURO.md` y `docs/PLAN-EQUIPO.md`. Comprueba que git sabe mi nombre y correo, trae lo último de main y explícame cómo vamos a trabajar.
4. La primera vez que tu IA suba algo, se abrirá una ventana para **iniciar sesión en GitHub**: hazlo tú (nunca le des tu contraseña a la IA).

---

## Trabajar con tu IA (cada día)

Tu IA lee sola `AGENTS.md` al abrir el proyecto (Claude Code, Copilot, Codex, Cursor). Ahí tiene los pasos de Git y la orden de explicártelos. Tú hablas normal:

| Tú dices | Tu IA hace |
|---|---|
| «Soy la persona B, empiezo con el gráfico de humedad» | Trae lo último de `main` y te crea la rama `feat/b-grafico-humedad` |
| «Actualiza mi rama» | Trae a tu rama lo nuevo de los demás (hazlo si llevas más de un día) |
| «Súbelo» / «ya he terminado» | Revisa qué has cambiado y deja fuera lo que no querías o es secreto. Pasa los tests, guarda, trae lo de los demás, sube y te da el enlace del PR con el título y la descripción |
| «Ya lo he unido» | Vuelve a `main`, lo actualiza y borra la rama |
| «Échale un vistazo al PR de Juan» | Descarga su rama, la prueba y te dice si está bien |
| «¿Puedo romper algo?» / «¿se ha perdido mi trabajo?» | Lo comprueba de verdad y te lo explica |
| Pegas un error de Git | Te explica qué significa y lo arregla sin borrar nada |

**Lo que haces tú en GitHub** (con el enlace que te da tu IA):
1. **Create pull request**.
2. Abajo del PR: si pone **«This branch has no conflicts with the base branch»** → **Merge pull request** → **Confirm merge**.
3. Si pone que hay conflictos, no lo unas: dile a tu IA «hay conflictos en el PR».
4. Si el cambio es grande o toca algo de lo que se encarga otra persona, avisa por el grupo o pide que alguien le eche un vistazo antes. No es obligatorio, pero ayuda.

**Si tu IA te propone `--force`, borrar cambios o «descartar» algo que no entiendes, dile que no** y que te lo explique. En `main` GitHub lo bloquearía igualmente.

Con una IA que no lea `AGENTS.md` sola (por ejemplo ChatGPT en el navegador), empieza con: «Lee AGENTS.md y docs/GIT-SEGURO.md de este proyecto y síguelos».

---

## Si algo sale mal

| Pasa esto | Qué significa | Qué hacer |
|---|---|---|
| *rejected* / *fetch first* al subir | Alguien subió antes a esa rama | Tu IA hace `git pull` y vuelve a subir. Nunca `--force` |
| *protected branch* | Intentabas subir directo a `main` y la seguridad lo ha parado | Tu IA pasa tus cambios a una rama y sube esa |
| *CONFLICT* | Tú y otra persona habéis cambiado las mismas líneas | Tu IA te enseña las dos versiones y os quedáis con lo bueno de ambas. Si no sabes qué quería la otra persona, pregúntale |
| Has trabajado en `main` sin querer | Aún no ha pasado nada: está solo en tu ordenador | Tu IA crea una rama y se lleva tus cambios |
| Algo de `main` se ha roto | Un PR ha metido un fallo | Avisa en el grupo. En ese PR, botón **Revert** |
| No sabes en qué rama estás o qué has cambiado | — | Pregúntale a tu IA: «¿en qué rama estoy y qué he cambiado?» |

---

## Para anieto23 (dueña del repositorio), una vez

### Invitar a los 6
Settings → **Collaborators** → **Add people**, rol **Write** (no Admin). Ahora están anieto23, efapro, mhjosemi-sudo y rmolino23-art: **faltan 2**.

### Protección de `main`
Settings → **Branches** → regla de `main` → **Edit**. Debe quedar así:
- [x] **Require a pull request before merging**
  - [ ] *Require approvals* → **sin marcar** (cada uno une su PR)
  - [ ] *Require review from Code Owners* → **sin marcar**
- [x] **Do not allow bypassing the above settings** (que la dueña tampoco suba directo sin querer)
- [ ] *Allow force pushes* → **sin marcar**
- [ ] *Allow deletions* → **sin marcar**

Pulsar **Save changes**. (Si se usa *Rulesets*: *Restrict deletions*, *Block force pushes* y *Require a pull request before merging* con 0 aprobaciones, y la lista de *Bypass* vacía).

### Comprobarlo
Que cualquiera le diga a su IA: «comprueba que no puedo subir directo a main sin estropear nada». Debe salir *protected branch*.
