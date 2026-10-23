---
name: respetar-carpetas
description: Antes de crear, editar o borrar cualquier archivo del repo, comprueba que es de la persona que está trabajando (A, B, C o D) y, si es de otra, para y avisa en vez de tocarlo. Úsala SIEMPRE antes de modificar archivos en este proyecto.
---

# Respetar las carpetas de cada persona

Cada persona es dueña de carpetas distintas (ver `docs/PLAN-EQUIPO.md`). No se pisan.

## Quién soy
Por la rama: `feat/a-...` = A, `feat/b-...` = B, `feat/c-...` = C, `feat/d-...` = D. Si la rama no lo dice, pregunta al usuario una vez.

## Propietarios (rutas bajo `agrotechEFA2026/` salvo las indicadas)
| Persona | Archivos suyos |
|---|---|
| A | `db/`, `api/`, `migrations/`; además gestiona los compartidos |
| B | `pages/dashboard.py`, `pages/historico.py`, `components/charts.py`, `components/sensor_card.py`, `state/dashboard_state.py` |
| C | `pages/parcelas.py`, `pages/sensores.py`, `pages/alertas.py`, `pages/login.py`, `components/layout.py`, `components/forms.py`, `state/gestion_state.py`, `state/auth_state.py`, `services/alertas.py` |
| D | `scripts/`, `firmware/`, `services/riego.py`, `services/telegram.py`, `services/export.py`, `Dockerfile`, `docs/hardware.md` |
| Compartidos (solo PR pequeño avisando; los gestiona A) | `agrotechEFA2026.py`, `rxconfig.py`, `pyproject.toml` |
| Cada uno | sus propios `tests/` y su sección de README y `docs/equipo/<letra>-*/` |

## Antes de cada edición
1. Mira la ruta del archivo. ¿Es de mi persona? Entonces sigue.
2. Si es de otra persona o compartido: **NO lo edites**. Dile al usuario qué archivo es, de quién es y qué cambio hacía falta, y propón alternativas: pedírselo a esa persona, abrir un PR pequeño a su rama, o resolverlo en una carpeta mía (por ejemplo, un adaptador en `services/`).
3. Solo edita un archivo ajeno si el usuario dice explícitamente que sí para ese archivo y ese cambio. Un sí anterior no vale para otros archivos.
4. Los archivos nuevos van dentro de mis carpetas. Si no encajan en ninguna, pregunta antes de crearlos.
5. Antes de empezar la sesión: `git fetch` y mira si alguien tocó mis archivos en `origin/main`.

## Nunca
- Cambiar el contrato (`docs/contrato.md`), el esquema de BBDD o el formato JSON de la API sin PR aprobado por A.
- Hacer push a `main` ni a ramas de otra persona.
- Renombrar, mover o borrar archivos ajenos para "arreglar" un import.
