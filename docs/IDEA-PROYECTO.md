# Idea del proyecto – leer antes de programar (todos)

> Propuesta del equipo (26-oct-2026). Lo que cambie el esquema de la base de datos o la API se aprueba en el grupo antes de unirlo (ver `docs/contrato.md` cuando exista).

## La idea en una frase
Una app (móvil, tablet y ordenador) donde el agricultor **dibuja su parcela a escala real**, coloca sus sensores en el plano, dice **qué cultivo** hay en cada zona y la app **compara cada lectura con los valores óptimos de ese cultivo**, le dice qué le falta («necesita más humedad») y le deja **actuar desde casa** («regar», «abrir ventanas»).

## Qué piden las bases (confirmado en agrotechstartup.com → Bases técnicas)
- **Obligatorio:** Python + **Reflex**, una base de datos, git + **GitHub** desde el primer día, software libre, licencia **GPL v3 o posterior**.
- **Base de datos:** vale **SQLite, MySQL, PostgreSQL o MariaDB**. MySQL **no** es obligatorio. Decisión propuesta: **SQLite para desarrollar y probar** (nadie instala nada) y MySQL/MariaDB opcional para la versión publicada. Reflex usa SQLModel/SQLAlchemy, así que cambiar de motor es cambiar `db_url` en `rxconfig.py`.
- **Mínimos:** web responsive, datos guardados, demo en directo con datos reales o simulados, código ordenado y comentado.
- **Git (puntúa):** commits frecuentes y descriptivos, una rama por funcionalidad, PR antes de unir.
- **Documentación:** README (propósito, instalación, ejecución), arquitectura breve y registro de la evolución.
- **Jurado:** funcionalidad y utilidad agro · código · diseño y facilidad de uso · docs y git · **innovación** · presentación.
- **Fechas:** entrega **8-dic-2026**, final **16-dic-2026** (Cooperativa Granada La Palma).

## Cómo funciona la app (flujo del usuario)
1. **Crea una parcela:** nombre, **interior** (invernadero) o **exterior** (campo), **ancho y largo en metros**.
2. **Coloca los sensores** en un plano 2D visto desde arriba, a escala (cuadrícula de 1 m). Cada sensor guarda su posición `x, y` en metros y la zona que cubre. Se pueden añadir más sensores después.
3. **Elige el cultivo** de cada zona o sensor (aguacate, mango, chirimoya, tomate…).
4. **Pulsa un sensor** y ve sus valores actuales junto a los óptimos del cultivo: «por debajo / bien / por encima», con texto e icono, no solo color.
5. **Actúa:** botones como «regar», «abrir ventilación», «sombrear». En la demo el simulador responde (la humedad sube poco a poco al regar). Cada acción queda guardada.

## Fases (de menos a más; no pasar a la siguiente sin cerrar la anterior)
| Fase | Qué | Hasta |
|---|---|---|
| 1 – Mínimos del reto | Login con roles, CRUD de parcelas y sensores, panel en tiempo real, histórico con gráficos, umbrales con aviso, API REST, simulador, tests | ~13 nov |
| 2 – Plano y cultivos | Parcela con medidas, plano con sensores colocados, tabla de cultivos con rangos óptimos, ficha del sensor comparando con lo óptimo | ~27 nov |
| 3 – Control | Botones de actuación según el tipo de parcela, simulador que reacciona, historial de acciones, recomendaciones | 4 dic (**congelar**) |

Si vamos justos de tiempo, se recorta la fase 3, nunca la 1.

## Quién se encarga de qué en esta idea (orientativo, todos tocan todo)
- **A – Backend:** tablas nuevas y API (ver «Datos» abajo), validación de posiciones dentro de la parcela.
- **B – Panel:** plano 2D de la parcela con los sensores, ficha del sensor frente a lo óptimo, gráficos.
- **C – Gestión:** formularios de parcela (tipo, medidas) y sensores (posición, cultivo), alertas cuando un valor sale del rango óptimo.
- **D – Sensores:** simulador realista (hora del día, interior más caliente, la humedad baja con el tiempo y **sube al regar**) que envía a la misma API que un ESP32.
- **E – Inteligencia:** comparación con los óptimos y recomendaciones («regar 20 min»), avisos por Telegram.
- **F – Calidad y entrega:** tests, despliegue, README/arquitectura y presentación que cuente esta idea.

## Datos (propuesta, pendiente de aprobar en el contrato)
Sobre las tablas sugeridas por las bases (`users, parcels, sensors, sensor_data, alerts`) se añaden:
- `parcels`: + `tipo` (`interior`/`exterior`), `ancho_m`, `largo_m`.
- `sensors`: + `pos_x_m`, `pos_y_m`, `radio_m` (zona que cubre), `cultivo_id`.
- `cultivos`: `id`, `nombre`, y por parámetro un mínimo y un máximo óptimos (temperatura, humedad del suelo, humedad del aire, luz), `fuente` (de dónde salen los datos).
- `acciones`: `id`, `parcel_id`, `tipo` (riego, ventilación…), `timestamp`, `user_id`.

## Cosas a tener en cuenta (importante)
1. **Interior y exterior no se controlan igual.** En exterior no se puede bajar la temperatura: solo regar (y como mucho sombrear). En interior hay además ventilación, calefacción, nebulización y sombreo. **La app solo muestra los botones que tienen sentido** en cada tipo de parcela.
2. **No inventar los valores óptimos.** Cada rango de cultivo sale de una fuente fiable (FAO, guías técnicas, profesorado de agraria de la EFA, técnicos de La Palma) y se guarda la fuente. Cultivos que encajan en la Costa Tropical: aguacate, mango, chirimoya, tomate de invernadero.
3. **Los botones de control son simulados** salvo que haya actuadores reales (relés, electroválvulas en un ESP32). En la presentación se dice claramente qué es real y qué simulado.
4. **Seguridad:** solo el rol agricultor puede actuar; el técnico/visor solo mira. Se valida todo lo que llega a la API (rangos, tipos, que el sensor sea de esa parcela y que su posición quede dentro de la parcela).
5. **Móvil primero:** el plano debe poder usarse en 375 px (zoom o lista de sensores como alternativa).
6. **El plano:** empezar con «clic en la cuadrícula para colocar». Arrastrar con el ratón queda para después, y antes hay que comprobar en la documentación de Reflex cómo se hace.
7. **Cambios del esquema o la API** afectan a todos: se avisa en el grupo antes de unirlos.
