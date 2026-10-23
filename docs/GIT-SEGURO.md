# Git seguro: que nadie pise el trabajo de nadie

Guía para los 6. Primero **cómo funciona** la seguridad, luego **cómo hacer los commits** cada día, y al final **qué hacer si algo sale mal**.

## Estado (revisado el 23-10-2026)

| Qué | Estado |
|---|---|
| Repositorio público (así la protección funciona sin pagar) | Hecho |
| `main` protegida: no se puede subir directo, hace falta PR con aprobación | Hecho (el PR #2 aparecía «bloqueado» hasta tener aprobación) |
| Al unir un PR se borra su rama en GitHub | Hecho |
| Colaboradores con permiso de escritura | **4 de 6**: anieto23 (dueña), efapro, mhjosemi-sudo, rmolino23-art. Faltan 2 |
| `.github/CODEOWNERS` con los usuarios reales | **Pendiente**: aún tiene `@PERSONA_X` y GitHub lo ignora |
| Prohibir `--force`, prohibir borrar `main` y «no saltarse las reglas» | Hay que confirmarlo: solo lo ve anieto23 (punto 1.3) |

---

## Cómo funciona (en 2 minutos)

**Hay dos copias del proyecto**: la tuya (tu ordenador) y la de GitHub (la del equipo). Lo que haces en tu ordenador no afecta a nadie hasta que lo subes (`git push`).

**Ramas.** `main` es la versión buena, la que se entrega. Cada tarea se hace en una **rama** propia (`feat/b-grafico-humedad`), que es una copia aparte. Puedes romper tu rama todo lo que quieras: `main` y las ramas de los demás no cambian.

**Git nunca borra en silencio.** Si subes y alguien había subido antes a la misma rama, GitHub **rechaza** tu subida («rejected») y te obliga a traer lo suyo primero (`git pull`). Git junta las dos versiones solo; únicamente pregunta (**conflicto**) si los dos habéis cambiado *las mismas líneas del mismo archivo*. Como cada uno tiene sus carpetas, eso casi nunca pasará.

**Pull request (PR).** Para meter tu rama en `main` abres un PR: «quiero unir esto». Las reglas de GitHub (no dependen de la buena voluntad de nadie):

1. **Nadie puede subir directo a `main`**, ni tú, ni tu IA, ni por error. Solo entra por PR.
2. **Un PR necesita 1 aprobación de otra persona.** Tú no puedes aprobar tu propio PR.
3. **Si cambias el PR después de aprobado**, la aprobación se anula y hay que volver a aprobar. Nadie cuela nada.
4. **`CODEOWNERS`** (cuando tenga los nombres): si tu PR toca la carpeta de otro, GitHub exige que apruebe **el dueño de esa carpeta** (o su compañero de revisión). Por eso no se puede cambiar lo de otro sin que se entere.
5. **Prohibido forzar (`--force`) y borrar `main`.** Son las dos únicas formas de destruir trabajo ya subido, y GitHub las bloquea.

**Todo queda en el historial.** Cada versión de cada archivo que haya estado en `main` sigue guardada. Si algo se rompe o se borra, se recupera.

**Tu IA** lee `AGENTS.md`, que le prohíbe forzar, tocar carpetas ajenas o resolver conflictos a ciegas. Aunque se equivoque, las reglas de GitHub de arriba la paran.

Resumen: **tus carpetas** (no os cruzáis) + **ramas** (cada uno en su copia) + **PR con aprobación** (nada entra sin que otro lo vea) + **sin `--force`** (nada se destruye).

---

## Primer día (cada persona, una vez)

1. **Acepta la invitación** al repositorio que te llega al correo de GitHub (si no te ha llegado, pídesela a anieto23).
2. **Descarga el proyecto.** En VS Code: *Ctrl+Shift+P* → «Git: Clone» → pega `https://github.com/anieto23/agrotechEFA2026.git` → elige carpeta → *Abrir*. (Si ya lo tenías descargado, ábrelo y en la terminal escribe `git pull` para traer lo último).
3. **Abre tu IA en esa carpeta** y pega este mensaje:
   > Soy la persona **X** del proyecto Agrotech y no sé usar git. Lee `AGENTS.md`, `docs/GIT-SEGURO.md` y `docs/PLAN-EQUIPO.md`. Comprueba que git sabe mi nombre y correo, trae lo último de main y explícame en 5 líneas cómo vamos a trabajar sin pisar a nadie.
4. La primera vez que tu IA suba algo, se abrirá una ventana para **iniciar sesión en GitHub**: hazlo tú (nunca le des tu contraseña a la IA).

A partir de ahí, cada día empieza con: «Soy la persona X, empiezo con <tarea>».

## Trabajar con tu IA (lo normal)

Tu IA lee sola `AGENTS.md` al abrir el proyecto: Claude Code (vía `CLAUDE.md`), Copilot (vía `.github/copilot-instructions.md`), Codex y Cursor. Ahí tiene los pasos exactos de git. Tú solo hablas normal:

| Tú dices | Tu IA hace |
|---|---|
| «Soy la persona B, empiezo con el gráfico de humedad» | Trae lo último de `main` y crea tu rama `feat/b-grafico-humedad` |
| «Súbelo» / «haz el commit» / «ya he terminado» | Revisa qué has cambiado, deja fuera lo que no es tuyo o es secreto, pasa los tests, hace el commit, trae lo de los demás, sube y te da el enlace del PR con el título y la descripción para pegar |
| «Ya me lo han aprobado» | Vuelve a `main`, lo actualiza y borra tu rama local |
| «Revisa el PR de Juan» | Descarga su rama, la prueba y te dice si está bien |
| Pega un error de git | Te explica qué pasa y lo arregla sin borrar nada |

**Lo único que haces tú**: abrir el PR en GitHub con tu cuenta (el enlace te lo da tu IA), pedir revisión a tu compañero y aprobar los PR de otros después de probarlos.

**Si tu IA te propone `--force`, borrar cambios o tocar la carpeta de otro, dile que no** y que siga `AGENTS.md`. Aunque lo intentara, GitHub lo bloquearía en `main`.

Con otra IA que no lea `AGENTS.md` sola (por ejemplo ChatGPT en el navegador), empieza con: «Lee AGENTS.md y docs/GIT-SEGURO.md de este proyecto y síguelos».

## Cómo hacer los commits a mano (lo que hace tu IA por dentro)

Si no usas IA, o para entender lo que hace, estos son los pasos.

### 1. Al empezar: trae lo último y crea tu rama
```
git switch main
git pull
git switch -c feat/<letra>-<tema>
```
Ejemplo: `feat/b-grafico-humedad`. **Una rama = una tarea pequeña** (de unas horas, no de una semana).

Si sigues una rama de ayer: `git switch feat/<letra>-<tema>` y luego `git merge main` (para traer lo nuevo de los demás).

### 2. Mientras trabajas: commits pequeños
```
git status                       # mira QUÉ archivos has cambiado
git add <tus archivos>           # solo los tuyos, uno a uno o tu carpeta
git commit -m "Añade gráfico de humedad del suelo"
git push -u origin feat/<letra>-<tema>    # la primera vez; luego basta con: git push
```
- **Mira `git status` antes de `git add`.** Si aparece un archivo que no es tuyo o que no querías tocar, no lo añadas y pregunta.
- **Mensaje:** en español, empieza por verbo, dice *qué* cambia: «Añade…», «Corrige…», «Quita…». Mal: «cambios», «arreglos», «asdf».
- **Haz `git push` a menudo** (al menos al acabar el día). Lo subido a tu rama está a salvo aunque se rompa tu ordenador.
- Nunca subas `.env`, contraseñas ni tokens (el `.gitignore` ya lo evita; no lo fuerces).

### 3. Para entregar: abre TÚ el PR
1. Antes, trae lo último de `main` a tu rama y comprueba que todo sigue funcionando:
   ```
   git fetch
   git merge origin/main
   python -m reflex run        # ¿arranca?
   python -m pytest            # ¿pasan los tests?
   git push
   ```
2. En GitHub sale el botón **Compare & pull request**. Ábrelo **con tu cuenta** (si lo abre otro, GitHub lo cuenta como suyo y podrías acabar aprobando tu propio trabajo).
3. Título claro y en la descripción: **qué cambia**, **cómo probarlo** y si toca algo fuera de tus carpetas.
4. A la derecha, **Reviewers** → tu compañero de rotación (A→B→C→D→E→F→A).
5. Cuando lo apruebe → **Merge pull request**. La rama se borra sola en GitHub. En tu ordenador:
   ```
   git switch main
   git pull
   git branch -d feat/<letra>-<tema>
   ```

### 4. Revisar el PR de otro
```
git fetch
git switch <su-rama>
python -m reflex run
```
Comprueba que hace lo que dice, que solo toca sus carpetas y que no hay claves en el código. Si todo bien → *Review changes* → **Approve**. Si no → **Request changes** explicando qué falla. Luego vuelve a tu rama (`git switch feat/<tu-rama>`).

---

## Si algo sale mal

| Pasa esto | Haz esto | Nunca |
|---|---|---|
| `git push` dice *rejected* o *fetch first* | `git pull` en tu rama y vuelve a subir | `git push --force` |
| *CONFLICT* al hacer pull o merge | Si es tu carpeta, mira las dos versiones y deja lo correcto de ambas. Si es de otro, **para y avísale** | Elegir «lo mío» a ciegas |
| Has trabajado en `main` sin querer | `git switch -c feat/<letra>-<tema>`: te llevas los cambios a una rama nueva | Intentar subir a `main` |
| Algo de `main` ha desaparecido o se ha roto | Avisa en el grupo. En el PR que lo causó, botón **Revert**: crea un PR que lo deshace | Copiar y pegar encima a mano |
| Tu IA propone `--force`, `reset --hard`, `rebase` o borrar ramas | Dile que no y que siga `AGENTS.md` | Aceptar sin entenderlo |
| Necesitas un cambio en la carpeta de otro | Díselo (qué función o dato necesitas). Si es urgente, PR pequeño y que lo apruebe él | Cambiarlo tú «que es un momento» |

---

## Parte para anieto23 (dueña del repositorio)

### 1.1 Invitar a los 2 que faltan
Settings → **Collaborators** → **Add people**, rol **Write** (no Admin). Que acepten desde el correo.

### 1.2 Poner los nombres en CODEOWNERS
Decidid quién es cada letra y cambiad cada `@PERSONA_X` de `.github/CODEOWNERS` por su usuario (por PR, como todo). Mientras no se haga, GitHub da error en ese archivo y la regla 4 no funciona.

### 1.3 Revisar la protección de `main`
Settings → **Branches** → regla de `main` → **Edit**. Debe estar así:
- [x] **Require a pull request before merging**
  - [x] **Require approvals** → `1`
  - [x] **Dismiss stale pull request approvals when new commits are pushed**
  - [x] **Require review from Code Owners**
- [x] **Require conversation resolution before merging**
- [x] **Do not allow bypassing the above settings** (si no, la dueña puede saltarse todo sin darse cuenta)
- [ ] *Allow force pushes* → **sin marcar**
- [ ] *Allow deletions* → **sin marcar**

(Si se usa *Rulesets* en vez de la regla clásica: *Restrict deletions*, *Block force pushes* y *Require a pull request* con lo mismo, y la lista de *Bypass* vacía.)
