# Guion común – leer antes del tuyo (todos)

## Preparar tu ordenador (una vez, 15 min)
1. Instalar: Python 3.12, git y VS Code. Comprobar: `python --version` y `git --version`.
2. Decirle a git quién eres: `git config --global user.name "Tu nombre"` y `git config --global user.email "tu@correo"`.
3. Ser invitado al repo de GitHub (lo hace anieto23: Settings → Collaborators) y clonarlo:
   `git clone https://github.com/anieto23/agrotechEFA2026.git`
4. Dentro de la carpeta: `pip install reflex` y `python -m reflex run` → abrir http://localhost:3000. Si ves el panel con 4 tarjetas, todo va.
5. Abrir tu IA (Claude Code, Copilot…) en esa carpeta y pegar al empezar cada día:
   > Soy la persona **X** del proyecto Agrotech y no sé mucho de git. Lee `AGENTS.md`, `docs/GIT-SEGURO.md`, `docs/PLAN-EQUIPO.md` y mi plan `docs/equipo/<tu carpeta>/GUION.md`. Trae lo último de main y dime en qué tarea estamos y qué toca hoy.
6. Lo de git (ramas, commits, PR) te lo explica y te lo hace tu IA: ver `docs/GIT-SEGURO.md`.

## Rutina de cada día (lo hace tu IA; tú le hablas normal)
1. «Soy la persona X, empiezo con <tarea>» → tu IA trae lo último de `main` y te crea una rama nueva para esa tarea.
2. Trabajas con tu IA y pruebas lo que hace (la web, el comando, el móvil).
3. «Súbelo» → tu IA guarda y sube los cambios y te da el enlace del PR. Lo abres y, si GitHub dice que no hay conflictos, pulsas **Merge** tú misma.
4. «Ya lo he unido» → tu IA vuelve a `main` y borra la rama. La siguiente tarea, rama nueva.

Todo el detalle (y qué hacer si algo falla) en `docs/GIT-SEGURO.md`.

## Si quieres que alguien mire tu PR (opcional)
No hace falta aprobación para unir, pero si el cambio es grande o toca lo de otra persona, pide un vistazo por el grupo. Quien lo mire se pregunta:
- ¿Lo he arrancado y hace lo que dice la descripción?
- ¿Rompe algo de lo que ya funcionaba?
- ¿Pasan los tests y no hay claves ni contraseñas en el código?

## Reglas de oro
- Todos podéis tocar todo, pero **nunca en `main`**: una rama `feat/<letra>-<tema>` por tarea, que dure poco.
- Un PR = una cosa pequeña (mejor 10 PR de 1 hora que 1 de 10 horas).
- Si vas a cambiar bastante algo de lo que se encarga otra persona, avísale por el grupo.
- Si el contrato (`docs/contrato.md`) te estorba, avisa al grupo; no lo cambies solo.
- Si algo se rompe en `main`, avisa en el grupo: se deshace con el botón **Revert** del PR que lo rompió.
- **Congelación de funciones: 4 dic.** Después solo errores.

## Fechas
Semanas: 1→30 oct · 2→6 nov · 3→13 nov · 4→20 nov · 5→27 nov · 6→4 dic · entrega **8 dic** · final **16 dic**.

## Reunión de equipo (15 min, 2 veces por semana)
Cada uno dice: qué terminé, qué hago ahora, qué necesito de otro. Se actualiza el tablero (GitHub Projects o el `PLAN.md`).
