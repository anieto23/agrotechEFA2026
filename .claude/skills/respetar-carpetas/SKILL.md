---
name: respetar-carpetas
description: Antes de crear, editar o borrar cualquier archivo del repo, comprueba que es de la persona que está trabajando (A, B, C, D, E o F) y, si es de otra, para y avisa en vez de tocarlo. Úsala SIEMPRE antes de modificar archivos en este proyecto.
---

# Respetar las carpetas de cada persona

Cada persona es dueña de carpetas distintas. No se pisan.

## Quién soy
Por la rama: `feat/a-...` = A, `feat/b-...` = B … `feat/f-...` = F. Si la rama no lo dice, pregunta al usuario una vez.

## Propietarios
La tabla buena está en `AGENTS.md`, apartado «Reparto» (y quién aprueba cada ruta, en `.github/CODEOWNERS`). Léela de ahí; no la copies aquí para que no se quede antigua.
Además: compartidos (`agrotechEFA2026.py`, `rxconfig.py`, `pyproject.toml`, `docs/contrato.md`) solo con PR pequeño avisando, los gestiona A; cada uno es dueño de sus propios `tests/`, su sección de README y su `docs/equipo/<letra>-*/`.

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
