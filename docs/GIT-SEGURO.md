# Git seguro: que nadie pise el trabajo de nadie

Tres capas. Con las tres, aunque alguien (o su IA) se equivoque, `main` no se rompe y nada se pierde.

1. **GitHub bloquea** lo peligroso: subir directo a `main`, forzar (`--force`), borrar `main`, unir sin aprobación.
2. **Cada persona es dueña de sus carpetas** (`docs/PLAN-EQUIPO.md`) y `.github/CODEOWNERS` obliga a que la dueña apruebe los cambios en ellas.
3. **Las IAs siguen las reglas** de `AGENTS.md` (apartado «Git sin pisar a nadie»).

---

## Parte 1 – La dueña del repositorio (anieto23), una sola vez

### 1.1 Que la protección funcione
El repositorio es **privado**. Con una cuenta gratuita de GitHub, la protección de ramas **no se aplica en repos privados** (se puede configurar, pero no bloquea). Elegid una:

- **A) Hacerlo público** (recomendado): el proyecto ya es software libre con licencia GPL v3 y el jurado podrá verlo. Settings → General → abajo del todo, *Danger Zone* → **Change visibility** → Public. Antes, comprobad que no hay contraseñas ni claves subidas.
- **B) Seguir privado con GitHub Pro gratis para estudiantes**: anieto23 pide el *GitHub Student Developer Pack* en https://education.github.com/pack con el correo del instituto. Cuando lo aprueben, la protección funciona en privados.

### 1.2 Invitar a los 6
Settings → **Collaborators** → **Add people** → usuario de cada uno. Rol **Write** (no Admin). Cada uno acepta la invitación desde su correo.

### 1.3 Proteger `main`
Settings → **Branches** → **Add classic branch protection rule** (si solo aparece *Rulesets*, ver más abajo).

- *Branch name pattern*: `main`
- [x] **Require a pull request before merging**
  - [x] **Require approvals** → `1`
  - [x] **Dismiss stale pull request approvals when new commits are pushed** (si alguien cambia el PR tras aprobarlo, hay que volver a aprobar)
  - [x] **Require review from Code Owners**
- [x] **Require conversation resolution before merging** (no se une con comentarios sin contestar)
- [x] **Do not allow bypassing the above settings** (ni la dueña se lo salta)
- [ ] *Allow force pushes* → **sin marcar**
- [ ] *Allow deletions* → **sin marcar**

Pulsar **Create**.

*Si sale Rulesets en vez de la regla clásica*: **New branch ruleset** → nombre `main`, *Enforcement status* **Active**, *Target branches* → **Include default branch**, y marcar: *Restrict deletions*, *Block force pushes*, *Require a pull request before merging* (1 aprobación, *Dismiss stale…*, *Require review from Code Owners*). Dejar vacía la lista de *Bypass*.

### 1.4 Limpieza automática
Settings → General → *Pull Requests* → [x] **Automatically delete head branches** (al unir un PR se borra su rama en GitHub; el trabajo ya está en `main`).

### 1.5 Poner los nombres en CODEOWNERS
En `.github/CODEOWNERS`, cambiar cada `@PERSONA_A`…`@PERSONA_F` por el usuario real de GitHub (por un PR, como todo).

### 1.6 Comprobarlo
Cualquiera intenta subir directo a `main`:
```
git switch main
git commit --allow-empty -m "Prueba de protección"
git push
```
Debe salir **rejected / protected branch**. Después deshacer la prueba en local: `git reset --hard origin/main` (solo en este caso, que no se ha subido nada).

---

## Parte 2 – Cada persona, cada día

**Al empezar**
```
git switch main
git pull
git switch -c feat/<letra>-<tema>        # rama nueva para la tarea
```
(o `git switch feat/<letra>-<tema>` y `git merge main` si sigues una de ayer)

**Mientras trabajas**: solo tus carpetas. Commits pequeños:
```
git status                # mira QUÉ vas a subir
git add <archivos tuyos>
git commit -m "Añade gráfico de humedad del suelo"
git push -u origin feat/<letra>-<tema>
```

**Para entregar**: en GitHub, **Compare & pull request** → describe qué cambia y cómo probarlo → pide revisión a tu compañero de rotación (A→B→C→D→E→F→A). Cuando lo apruebe, **Merge**.

**Revisar el PR de otro**: arráncalo (`git fetch` + `git switch <su rama>` + `python -m reflex run`), comprueba que hace lo que dice y que solo toca sus carpetas. Entonces *Approve*.

---

## Si algo sale mal

| Pasa esto | Haz esto | Nunca |
|---|---|---|
| `git push` dice *rejected* o *fetch first* | `git pull` en tu rama y vuelve a subir | `git push --force` |
| *CONFLICT* al hacer pull o merge | Si es tu carpeta, mira las dos versiones y quédate con lo correcto de ambas. Si es de otro, **para y avísale** | Elegir «lo mío» a ciegas |
| Te has puesto a trabajar en `main` sin querer | `git switch -c feat/<letra>-<tema>`: te llevas los cambios a una rama nueva | Subir a `main` |
| Algo que estaba en `main` ha desaparecido | Avisad en el grupo: está en el historial y se recupera con un PR que lo revierta (*Revert* en el PR original) | Copiar y pegar a mano encima |
| Tu IA propone `--force`, `reset --hard`, `rebase` o borrar ramas | Dile que no y que siga `AGENTS.md` | Aceptar sin entenderlo |
