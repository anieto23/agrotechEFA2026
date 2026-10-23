# Plan del grupo C – Gestión, alertas y experiencia de uso

**Misión:** que un agricultor pueda **entrar, dar de alta su parcela y sus sensores, fijar límites y enterarse cuando algo va mal**, desde el móvil. Es la mitad del baremo de funcionalidad (CRUD, roles y alertas son requisitos mínimos).
**Carpetas de C:** `pages/login.py`, `pages/parcelas.py`, `pages/sensores.py`, `pages/alertas.py`, `components/layout.py`, `components/forms.py`, `state/gestion_state.py`, `state/auth_state.py`, `services/alertas.py`.
**Depende de A:** modelos y funciones de la BBDD (semana 1–2) y el login de la API. Hasta entonces trabajáis con datos de ejemplo.
**Entrega a los demás:** el menú y el tema (todas las páginas de B lo usan) y `alertas.evaluar()` (lo llama el endpoint de A).

## Contratos de C (en `docs/contrato.md`)
```python
# services/alertas.py  – C lo escribe, A lo llama al guardar cada lectura
def evaluar(session, lectura) -> Alerta | None   # crea la alerta si supera el umbral

# Roles
"agricultor": ve y edita sus parcelas y sensores, reconoce alertas
"tecnico":    solo ve (parcelas, datos, alertas); no crea ni borra
```
Modelo de umbral (campos en `sensors`): `umbral_min`, `umbral_max`, `activo`.

---
## Tarea C1 – Marco de la app: menú, tema y móvil (semana 1) · lo primero, porque lo usan todos
- **Archivo:** `components/layout.py` con `pagina(contenido, titulo)`: barra lateral en ordenador, **barra inferior en móvil**, cabecera con usuario y rol, indicador de alertas sin leer.
- **Tema:** reaprovechar el oscuro actual (#272727 / #CACACA) y añadir interruptor claro/oscuro. Definir colores en un único sitio para que B y D no inventen los suyos.
- **Páginas del menú:** Panel · Histórico · Parcelas · Sensores · Alertas.
- **Listo cuando:** se navega entre páginas vacías en ordenador y móvil (se prueba a 375 px), con la página activa resaltada.
- **Tú haces:** abrirlo en tu móvil y decir si se ve bien.

## Tarea C2 – Login y roles (semanas 2–3, junto con A)
- **Archivos:** `pages/login.py`, `state/auth_state.py`.
- **Qué hace:** formulario de usuario y contraseña, errores claros, cierre de sesión. Guarda el usuario en el `State`. Las páginas de gestión comprueban el rol: el técnico ve los botones de crear/borrar desactivados o ocultos.
- **Seguridad:** contraseñas con hash (A lo implementa en la BBDD); nunca texto plano. Usuarios de demo: `agricultor@demo` y `tecnico@demo`, creados por el `seed` de A.
- **Listo cuando:** sin sesión te redirige a `/login`; con el técnico no se puede borrar nada; test de ambos casos.

## Tarea C3 – Parcelas (semana 2–3)
- **Archivo:** `pages/parcelas.py`.
- **Qué hace:** tabla de parcelas (nombre, cultivo, superficie, coordenadas, nº de sensores, estado), formulario para crear y editar, borrar con confirmación ("se borrarán también sus sensores y datos").
- **Cultivo:** desplegable con los de `data/cultivos.json` de D (tomate, aguacate, mango, chirimoya), porque la recomendación de riego de D lo usa.
- **Extra barato:** mini mapa con OpenStreetMap incrustado en la ficha de la parcela, centrado en las coordenadas.
- **Validaciones:** nombre obligatorio y único por usuario, coordenadas en rango, superficie > 0.
- **Listo cuando:** CRUD completo funciona, los errores salen en el formulario y hay tests de las validaciones.

## Tarea C4 – Sensores y umbrales (semana 3)
- **Archivo:** `pages/sensores.py`.
- **Qué hace:** lista de sensores por parcela; alta con tipo (temperatura, humedad aire, humedad suelo, luz), unidad automática por tipo, **umbral mínimo y máximo**, activo/inactivo.
- **Clave de API:** al crear un sensor se genera su `X-API-Key` y se muestra **una sola vez** con botón de copiar y opción de regenerarla. Es la clave que D pone en el ESP32.
- **Umbrales por defecto** sensatos según el tipo (p. ej. suelo 30–70 %) para que no haya que escribirlos siempre.
- **Estado de conexión:** "último dato hace 2 min" en verde, y en rojo si lleva más de 10 min sin llegar nada (sensor caído).
- **Listo cuando:** crear un sensor desde la web y enviarle datos con la clave hace que aparezcan en el panel de B.

## Tarea C5 – Motor de alertas (semana 3–4) · la parte más importante de C
- **Archivo:** `services/alertas.py`.
- **`evaluar(session, lectura)`:** compara con el umbral; si lo supera y no hay ya una alerta abierta del mismo sensor, la crea (no una por cada lectura). Cuando el valor vuelve al rango, la cierra sola.
- **Estados:** `abierta → reconocida → resuelta`. Guarda hora de inicio, valor máximo alcanzado y quién la reconoció.
- **Aviso externo:** llama a `telegram.avisar()` de D (con el límite de 1 cada 30 min).
- **Alerta de sensor caído:** tarea periódica que mira los sensores sin datos recientes.
- **Tests (obligatorios, es lógica con ramas):** dentro/fuera del umbral, alerta repetida, cierre automático, sensor sin umbral.
- **Listo cuando:** `--evento sequia` del simulador de D abre una alerta, llega el Telegram, se ve en la página y se cierra al volver a la normalidad.

## Tarea C6 – Página de alertas y avisos en pantalla (semana 4)
- **Archivo:** `pages/alertas.py` + insignia con el número de alertas abiertas en el menú.
- **Qué hace:** lista filtrable (abiertas / reconocidas / resueltas, parcela, fechas), botón "Reconocer", detalle con la gráfica del sensor alrededor del momento de la alerta (reusa el componente de B), aviso emergente (toast) cuando entra una nueva con la página abierta.
- **Accesibilidad:** el estado no se indica solo con el color (también icono y texto).

## Tarea C7 – Pulido y accesibilidad (semana 5)
- Estados vacíos con ayuda ("Aún no tienes parcelas, crea la primera"), mensajes de carga y de error.
- Que todo se pueda usar con teclado y tenga etiquetas.
- Revisión en móvil y tableta de todas las páginas, incluidas las de B y D.

## Calendario de C
| Semana | Entrega |
|---|---|
| 1 (→30 oct) | C1 menú, tema y móvil con páginas vacías |
| 2 (→6 nov) | C3 parcelas con datos de ejemplo; C2 pantalla de login |
| 3 (→13 nov) | C2 conectado a la API de A, C3 con la BBDD real, C4 sensores y claves |
| 4 (→20 nov) | C5 motor de alertas, C6 página de alertas |
| 5 (→27 nov) | C7 pulido, tests, sección del README |
| 6 (→4 dic) | Congelar; ensayo de la demo del flujo alta → alerta |

## Reparto interno de C (si sois varias personas)
Una persona hace C1+C2 (marco y acceso), otra C3+C4 (formularios), otra C5+C6 (alertas). C1 va primero: bloquea a todos los demás.

## Riesgos de C
- **Formularios de Reflex largos y repetitivos** → un único componente `forms.py` reutilizable, para que no haya 4 formularios copiados.
- **Cambia el modelo de A y se rompe la gestión** → no tocar la BBDD directamente; usar solo las funciones de `db/`.
- **Alertas duplicadas** → regla "una abierta por sensor", con test.
