# Guion común – leer antes del tuyo (todos)

## Preparar tu ordenador (una vez, 15 min)
1. Instalar: Python 3.12, git y VS Code. Comprobar: `python --version` y `git --version`.
2. Decirle a git quién eres: `git config --global user.name "Tu nombre"` y `git config --global user.email "tu@correo"`.
3. Ser invitado al repo de GitHub (lo hace anieto23: Settings → Collaborators) y clonarlo:
   `git clone https://github.com/anieto23/agrotechEFA2026.git`
4. Dentro de la carpeta: `pip install reflex` y `python -m reflex run` → abrir http://localhost:3000. Si ves el panel con 4 tarjetas, todo va.
5. Abrir Claude Code en esa carpeta y pegar al empezar cada día:
   > Soy la persona **X** del proyecto Agrotech. Lee `AGENTS.md`, `docs/PLAN-EQUIPO.md` y mi plan `docs/equipo/<tu carpeta>/GUION.md`. Haz `git pull` y dime en qué tarea estamos y qué toca hoy.

## Rutina de cada día (10 min)
1. `git pull`. Mirar los PR abiertos.
2. Pedir a Claude la tarea del día de tu guion.
3. Probar lo que ha hecho (la web, el comando, el móvil). Si funciona → "súbelo como PR".
4. Revisar **un PR de otra persona** (rotamos: A→B→C→D→A). Aprobar solo si lo has probado.

## Cómo revisar un PR (3 preguntas)
- ¿Lo he arrancado y hace lo que dice la descripción?
- ¿Solo toca las carpetas de su dueño?
- ¿Pasan los tests y no hay claves ni contraseñas en el código?

## Reglas de oro
- Nunca en `main`: rama `feat/<letra>-<tema>`.
- Un PR = una cosa pequeña (mejor 10 PR de 1 hora que 1 de 10 horas).
- Si el contrato (`docs/contrato.md`) te estorba, avisa al grupo; no lo cambies solo.
- Si algo se rompe, avisa en el grupo y no lo arregles en carpeta ajena.
- **Congelación de funciones: 4 dic.** Después solo errores.

## Fechas
Semanas: 1→30 oct · 2→6 nov · 3→13 nov · 4→20 nov · 5→27 nov · 6→4 dic · entrega **8 dic** · final **16 dic**.

## Reunión de equipo (15 min, 2 veces por semana)
Cada uno dice: qué terminé, qué hago ahora, qué necesito de otro. Se actualiza el tablero (GitHub Projects o el `PLAN.md`).
