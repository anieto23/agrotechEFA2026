# Guion de C – Gestión, alertas y experiencia de uso

Plan completo y detallado en `PLAN.md` (esta misma carpeta). Este guion es la versión corta para trabajar día a día.
**Tus carpetas:** `pages/login.py`, `pages/parcelas.py`, `pages/sensores.py`, `pages/alertas.py`, `components/layout.py`, `components/forms.py`, `state/gestion_state.py`, `state/auth_state.py`, `services/alertas.py`.
Lee antes `docs/GUION-COMUN.md` y `AGENTS.md`.

## Semana 1 (→30 oct) – tu marco desbloquea a B y D
> Soy C. Lee `docs/equipo/C-gestion/PLAN.md`. Haz la tarea C1: `components/layout.py` con una función `pagina(contenido, titulo)` que ponga barra lateral en ordenador y barra inferior en móvil, página activa resaltada, cabecera con usuario y rol, y un único archivo de colores. Páginas vacías: Panel, Histórico, Parcelas, Sensores, Alertas. Pruébalo a 375 px.
**Tú:** abre http://localhost:3000 en tu móvil y di si se ve bien. Aprobad B y tú los colores.

## Semana 2 (→6 nov) – parcelas y login (con datos de ejemplo)
> Tarea C3: `pages/parcelas.py` con tabla, formulario de alta/edición y borrado con confirmación; cultivos desde `data/cultivos.json`. Validaciones con mensajes en el formulario y tests. Usa datos de ejemplo hasta que A termine `db/`.
> Tarea C2 (pantalla): `pages/login.py` y `state/auth_state.py` con el formulario y la redirección.

## Semana 3 (→13 nov) – conectar con la base de datos y sensores
> Conecta parcelas y login con las funciones de `db/` de A. Tarea C4: `pages/sensores.py` con alta de sensor, umbrales mínimo y máximo por defecto según el tipo, y su clave `X-API-Key` mostrada una sola vez con botón de copiar. Estado del sensor: "último dato hace X min" y en rojo si lleva más de 10 min sin datos.

## Semana 4 (→20 nov) – alertas
> Tarea C5: `services/alertas.py` con `evaluar(session, lectura)`: una sola alerta abierta por sensor, estados abierta → reconocida → resuelta, cierre automático al volver al rango, aviso por `telegram.avisar()` de D (máx. 1 cada 30 min). Tests de todos los casos. Tarea C6: `pages/alertas.py` con filtros, botón Reconocer, gráfica del sensor (componente de B), toast al llegar una nueva e insignia en el menú.

## Semana 5 (→27 nov) – pulido
> Tarea C7: estados vacíos, cargas, errores, uso con teclado, etiquetas, que nada dependa solo del color. Revisar móvil y tableta en todas las páginas.

## Semana 6 (→4 dic)
Congelar. Ensayar el recorrido "alta de parcela → alta de sensor → llega un dato → salta una alerta → llega Telegram". Tu sección del README con capturas.

## Si sois varias en C
Persona 1: layout + login · Persona 2: parcelas + sensores · Persona 3: alertas. El layout va primero.

## Qué entregas / qué necesitas
| Entregas | A quién |
|---|---|
| Menú, tema y `pagina()` | B y D (30 oct) |
| `alertas.evaluar()` | A, que lo llama al guardar lecturas (20 nov) |
| **Necesitas** | **de quién** |
| Modelos y funciones de `db/` | A (30 oct) |
| Login/roles en la API | A (13 nov) |
| `telegram.avisar()` | D (20 nov) |
| Componente de gráfica | B (20 nov) |

## Riesgos
- Formularios repetidos → un único `forms.py`.
- Alertas duplicadas → regla "una abierta por sensor", con test.
- Tocar la BBDD directamente → solo con las funciones de `db/`.
