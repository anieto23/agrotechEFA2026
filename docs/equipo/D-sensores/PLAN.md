# Plan de D – Sensores e inteligencia

**Misión:** que la demo de la final tenga datos *reales* y un panel que "piensa". Es la parte que nos separa de los demás equipos.
**Carpetas de D:** `scripts/`, `firmware/`, `services/riego.py`, `services/telegram.py`, `services/export.py`, `Dockerfile`, `docs/hardware.md`.
**Depende de A:** el endpoint `POST /api/sensors/{sensor_id}/data` (semana 2). Hasta entonces el simulador imprime por pantalla.
**Entrega a los demás:** un flujo de datos constante (para que B pinte gráficos), `riego.recomendar()` (para B) y `telegram.avisar()` (para C).

## Contrato que D debe respetar (fijado en `docs/contrato.md`)
```json
POST /api/sensors/{sensor_id}/data
Cabecera: X-API-Key: <clave del sensor>
{"sensor_id": 3, "timestamp": "2026-11-02T10:15:00+01:00", "type": "soil_moisture", "value": 41.5, "unit": "%"}
```
Tipos: `temperature` (ºC), `air_humidity` (%), `soil_moisture` (%), `light` (lx).

---
## Tarea D1 – Simulador (semana 1–2) · 100 % Claude
- **Archivo:** `scripts/gen_sample_data.py` (+ `scripts/sim_config.json`).
- **Qué hace:** manda cada N segundos lecturas de 4 sensores por parcela. Curvas realistas: temperatura sinusoidal 8–34 ºC con pico a las 15:00 y ruido; luminosidad 0 de noche y hasta 80 000 lx a mediodía con nubes aleatorias; humedad del suelo que baja despacio y **sube de golpe al "regar"**; humedad ambiental inversa a la temperatura.
- **Opciones:** `--url`, `--parcelas 3`, `--intervalo 5`, `--rapido` (simula un día en 2 min para la demo), `--historico 14` (rellena 14 días de historia de golpe para que los gráficos tengan datos), `--evento sequia` (fuerza una alerta en directo).
- **Listo cuando:** `python scripts/gen_sample_data.py --historico 14` llena la BBDD y `--rapido` mueve las tarjetas del panel. Test: los valores quedan siempre en rango.
- **Tú haces:** ejecutarlo, ver que los números parecen de verdad y decirle "más/menos ruido".

## Tarea D2 – Sensor real ESP32 (semanas 2–4) · tú haces el montaje, Claude el código
**Material (unos 25–35 €, preguntad en clase si hay):**
| Pieza | Para qué |
|---|---|
| ESP32 DevKit (WiFi) | cerebro |
| DHT22 o BME280 | temperatura y humedad ambiental |
| Sensor capacitivo de humedad de suelo v1.2 | humedad del suelo (entrada analógica) |
| BH1750 | luminosidad (I²C) |
| Protoboard, cables, USB, maceta con tierra | montaje y demo |

- **Firmware:** `firmware/esp32/main.py` (MicroPython) o Arduino, lo que prefiráis. Se conecta al WiFi, lee los 4 sensores cada 30 s y hace `POST` con su `X-API-Key`.
- **Calibración del suelo:** se mide el valor con el sensor al aire (0 %) y en un vaso de agua (100 %) y se guardan los dos números en `firmware/esp32/config.py`. Sin esto el dato no vale.
- **Fallo de WiFi:** guarda las lecturas en memoria y las envía al volver; si no, la demo se rompe con el WiFi del aula.
- **Plan B si no hay material:** `scripts/esp32_virtual.py` que se comporta igual que el firmware. La demo no depende del hardware.
- **Listo cuando:** el sensor real y el simulador aparecen en el mismo panel, y mojar la tierra de la maceta sube la humedad en pantalla en menos de 1 minuto.
- **Tú haces:** conseguir las piezas, conectar los cables (Claude te da el esquema de pines en `docs/hardware.md`), calibrar, llevar el montaje a la final.

## Tarea D3 – Recomendación de riego (semanas 3–4) · 100 % Claude
- **Archivo:** `services/riego.py` con `recomendar(parcela_id) -> {"regar": bool, "minutos": int, "motivo": str, "confianza": ...}`.
- **Lógica (reglas simples y explicables, que el jurado entiende):**
  1. Humedad del suelo media de las últimas 3 h bajo el umbral del cultivo → regar.
  2. Minutos = déficit respecto al objetivo × caudal del riego × factor del cultivo.
  3. Se corrige con la **previsión de lluvia y temperatura de Open-Meteo** (API gratuita, sin clave; Motril: lat 36.75, lon −3.52). Si llueve más de 2 mm en 24 h → "no regar, lloverá".
  4. Cultivos de ejemplo en `data/cultivos.json`: tomate, aguacate, mango, chirimoya (Costa Tropical).
- **Salida en lenguaje humano:** "Regar 18 min hoy antes de las 8:00: suelo al 28 % (mínimo 35 %), 31 ºC, sin lluvia prevista."
- **Listo cuando:** tests con casos (suelo seco → regar; suelo seco + lluvia → no; suelo húmedo → no) y el texto aparece en la tarjeta que dibuja B.
- **Tú haces:** decidir cultivos y umbrales con alguien que sepa de campo (profe de la rama agraria) y validar que las cifras son razonables.

## Tarea D4 – Avisos por Telegram (semana 4) · Claude + 5 min tuyos
- **Archivo:** `services/telegram.py` con `avisar(mensaje)`, usando la API de bots por HTTP.
- **Tú haces (único paso manual):** crear el bot con @BotFather, pasar el token y el chat id a Claude. **El token va en `.env`, nunca al repo.**
- **Cuándo avisa:** C llama a `avisar()` cuando se dispara una alerta. Mensaje: "⚠️ Parcela 2: humedad del suelo 22 % (mínimo 35 %)". Sin spam: máximo 1 aviso por alerta cada 30 min.
- **Listo cuando:** la alerta forzada con `--evento sequia` te llega al móvil.

## Tarea D5 – Exportar, despliegue y vídeo (semanas 5–6)
- `services/export.py`: botón "Descargar CSV" del histórico (rango de fechas) y un informe PDF de una página con gráficos y la recomendación.
- `Dockerfile` y despliegue público (Reflex + SQLite en un servidor gratuito o el de clase). Claude investiga las opciones y os dice cuál; **vosotros decidís dónde se publica**.
- Vídeo de demo (2 min): Claude escribe el guion y la lista de planos; tú grabas pantalla y sensor.

## Calendario de D
| Semana | Entrega |
|---|---|
| 1 (→30 oct) | D1 simulador v1 imprimiendo; pedir material para D2 |
| 2 (→6 nov) | D1 enviando a la API y `--historico`; material conseguido |
| 3 (→13 nov) | D2 sensor midiendo y enviando; calibrado |
| 4 (→20 nov) | D3 riego + D4 Telegram |
| 5 (→27 nov) | D5 exportar y despliegue; tests de todo lo tuyo |
| 6 (→4 dic) | Congelar; vídeo; sección de hardware en README y doc de arquitectura |

## Riesgos de D
- **El WiFi de clase bloquea el ESP32** → llevar el móvil como punto de acceso y tener `esp32_virtual.py`.
- **Sensor de suelo da valores raros** → calibración (D2) y filtrar con la media de 5 lecturas.
- **Open-Meteo no responde en la demo** → guardar la última previsión y usarla si falla.
