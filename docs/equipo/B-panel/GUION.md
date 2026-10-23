# Guion de B – Panel y gráficos

**Eres la cara del proyecto:** lo primero que ve el jurado es tu panel. Debe verse limpio, rápido y bien en móvil.
**Tus carpetas:** `pages/dashboard.py`, `pages/historico.py`, `components/charts.py`, `components/sensor_card.py`, `state/dashboard_state.py`.
Usas el menú y el tema que hace C (`components/layout.py`). Lee antes `docs/GUION-COMUN.md` y `AGENTS.md`.

## Semana 1 (→30 oct) – maqueta con datos de ejemplo
**B1. Reorganizar lo que ya existe.** El panel actual (4 tarjetas) está todo en un archivo. Pega a Claude:
> Soy B. Mueve la tarjeta de sensor a `components/sensor_card.py` y la página a `pages/dashboard.py`, sin cambiar cómo se ve. Cabe en el menú de C cuando exista. Que los colores salgan de un único sitio. Ejecuta y confirma que se ve igual.
**B2. Maqueta con datos falsos.** > Haz el panel con 2 parcelas de ejemplo (datos en un JSON de prueba), tarjetas por sensor con valor, unidad, hora de la última lectura y color según estado (normal / aviso / alerta). Diseño de 1 columna en móvil, 2 en tablet y 4 en ordenador.
No esperas a A: trabajas con el JSON hasta que haya API.

## Semana 2 (→6 nov) – tiempo real
**B3. Datos de verdad.** > Sustituye el JSON por `GET /api/dashboard` de A (o las funciones de `db/`). El `DashboardState` pide los datos cada 5 s con un evento en segundo plano y actualiza las tarjetas. Indica "actualizado hace Xs" y muestra el estado "sin conexión" si falla.
**B4. Selector de parcela.** > Desplegable para cambiar de parcela y que se recuerde la última elegida.

## Semana 3 (→13 nov) – histórico
**B5. Gráficos.** > Crea `components/charts.py` con un gráfico de líneas por sensor (recharts de Reflex) y `pages/historico.py`: elegir parcela, sensores y rango de fechas (hoy, 7 días, 30 días, personalizado). Líneas de umbral mínimo y máximo dibujadas, y tooltip con valor y hora.
**B6. Rendimiento.** > Si hay muchos puntos, agrega por hora/día en el servidor y limita a ~500 puntos por gráfica.

## Semana 4 (→20 nov) – pulido visual
**B7.** > Panel resumen arriba: nº de parcelas, sensores activos, alertas abiertas (de C). Tarjeta de recomendación de riego (de D): "Regar 18 min hoy: suelo al 28 %". Animación suave al cambiar un valor. Estados vacíos y de carga.
**B8. Reutilizable.** El componente de gráfica lo usa C en la página de alertas: documenta sus parámetros en el propio archivo.

## Semana 5 (→27 nov) – móvil y extras
**B9. Responsive de verdad.** > Revisa todas las páginas a 375 px, 768 px y 1280 px. Que no haya scroll horizontal ni texto cortado.
**B10. PWA instalable** (icono, nombre, `manifest`, abrir a pantalla completa en el móvil).
**B11. Botón "Descargar CSV/PDF"** que llama a `services/export.py` de D.
**B12. Modo claro/oscuro** (con C).

## Semana 6 (→4 dic)
Congelar la interfaz. Hacer las capturas para el README, escribir tu sección y ensayar el recorrido de la demo (panel → histórico → alerta).

## Qué entregas / qué necesitas
| Entregas | A quién |
|---|---|
| `charts.py` documentado | C |
| Capturas del panel | todos, para el README |
| **Necesitas** | **de quién** |
| `GET /api/dashboard` | A (semana 2) |
| `riego.recomendar()` | D (semana 4) |
| Menú y tema | C (semana 1) |

## Riesgos
- Gráficas lentas con muchos datos → agregar en servidor (B6).
- Mala vista en móvil → probarlo en tu móvil cada semana, no solo al final.
