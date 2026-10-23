# Guion de D – Sensores e inteligencia

Plan completo en `PLAN.md` (esta misma carpeta). Este guion es la versión corta para el día a día.
**Tus carpetas:** `scripts/`, `firmware/`, `services/riego.py`, `services/telegram.py`, `services/export.py`, `Dockerfile`, `docs/hardware.md`.
Lee antes `docs/GUION-COMUN.md` y `AGENTS.md`.

## Semana 1 (→30 oct) – simulador y material
> Soy D. Lee `docs/equipo/D-sensores/PLAN.md`. Haz la tarea D1: `scripts/gen_sample_data.py` con curvas realistas (temperatura 8–34 ºC con pico a las 15:00, luz que sube y baja con el día y las nubes, humedad del suelo que baja y sube al "regar", humedad ambiental inversa a la temperatura). Opciones `--url`, `--parcelas`, `--intervalo`, `--rapido`, `--historico 14` y `--evento sequia`. Por ahora imprime en pantalla en el formato JSON del contrato. Test de que los valores quedan en rango.
**Tú, esta semana:** preguntar en clase si hay ESP32 y sensores (ESP32 DevKit, DHT22/BME280, sensor de suelo capacitivo, BH1750). Si no hay, pedir a Claude la lista de compra con precios y que el equipo decida.

## Semana 2 (→6 nov) – enviar a la API
> Cuando A tenga el endpoint, haz que el simulador envíe con `POST /api/sensors/{id}/data` y la cabecera `X-API-Key`. Añade `--historico 14` que rellena 14 días. Muéstrame cómo ver los datos en el panel de B.
**Tú:** probar, y conseguir las piezas.

## Semana 3 (→13 nov) – sensor real
> Tarea D2: escribe `firmware/esp32/main.py` (MicroPython) que lea los sensores cada 30 s y envíe con su clave, guarde lecturas si cae el WiFi y use la calibración de `config.py`. Dame el esquema de pines en `docs/hardware.md` y los pasos para volcarlo al ESP32. Crea además `scripts/esp32_virtual.py` como plan B.
**Tú:** montar los cables, volcar el firmware, calibrar (sensor al aire = 0 %, en agua = 100 %), probar mojando la maceta.

## Semana 4 (→20 nov) – inteligencia
> Tarea D3: `services/riego.py` con `recomendar(parcela_id)`; reglas por cultivo (`data/cultivos.json`: tomate, aguacate, mango, chirimoya), previsión de Open-Meteo para Motril (36.75, −3.52), texto en lenguaje humano. Tests: suelo seco, suelo seco con lluvia, suelo húmedo.
> Tarea D4: `services/telegram.py` con `avisar(mensaje)`, token por `.env`, máximo 1 aviso cada 30 min.
**Tú:** crear el bot con @BotFather, pasar el token y chat id **solo a tu `.env`** (nunca a git), y validar con el profe agrario que los umbrales de cultivo son razonables.

## Semana 5 (→27 nov) – exportar y publicar
> Tarea D5: `services/export.py` (CSV por rango de fechas e informe PDF de una página), `Dockerfile` y propuesta de dónde desplegar gratis; yo decido.
**Tú:** decidir dónde se publica y probar la web pública desde el móvil.

## Semana 6 (→4 dic)
Congelar. Vídeo de 2 min: Claude escribe el guion y los planos, tú grabas pantalla y sensor. Tu sección de hardware en README y arquitectura.

## Qué entregas / qué necesitas
| Entregas | A quién |
|---|---|
| Flujo de datos del simulador | B y A para probar (6 nov) |
| `riego.recomendar()` | B (20 nov) |
| `telegram.avisar()` | C (20 nov) |
| CSV/PDF | B, botón de descarga (27 nov) |
| **Necesitas** | **de quién** |
| Endpoint de ingestión | A (6 nov) |
| Claves de sensor | C (alta de sensores, 13 nov) |

## Riesgos
- WiFi de clase bloquea el ESP32 → usar el móvil como punto de acceso y tener el plan B virtual.
- Sensor de suelo da valores raros → calibrar y filtrar con la media de 5 lecturas.
- Open-Meteo no responde en la demo → guardar la última previsión.
- El token de Telegram nunca al repo.
