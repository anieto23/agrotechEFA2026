# Hardware: aparato con ESP32

Un **aparato** (ESP32 con 4 sondas, uno por sector) envía cada 30 s sus lecturas a `POST /api/sensors/{id}/data` con su `X-API-Key`, igual que el simulador. Sin hardware se usa `scripts/esp32_virtual.py`.

## Material (≈ 25–35 €)
| Pieza | Para qué |
|---|---|
| ESP32 DevKit (WiFi) | cerebro |
| DHT22 (o BME280) | temperatura y humedad del aire |
| Sensor capacitivo de humedad de suelo v1.2 | humedad del suelo (analógico) |
| BH1750 | luz (I²C) |
| Protoboard, cables dupont, cable USB, maceta con tierra | montaje y demo |

## Pines (los de `firmware/esp32/config.py`)
| Sensor | Pin del sensor | Pin del ESP32 |
|---|---|---|
| DHT22 | VCC / DATA / GND | 3V3 / **GPIO4** / GND (resistencia 10 kΩ entre DATA y 3V3 si el módulo no la lleva) |
| Suelo capacitivo | VCC / AOUT / GND | 3V3 / **GPIO34** / GND |
| BH1750 | VCC / SDA / SCL / GND | 3V3 / **GPIO21** / **GPIO22** / GND |

El GPIO34 solo es de entrada y admite ADC aunque el WiFi esté activo (no uses GPIO de ADC2).

## Poner el firmware
1. Instalar MicroPython en el ESP32 (una vez): `pip install esptool mpremote`, y desde https://micropython.org/download/ESP32_GENERIC/ el `.bin`; luego
   `esptool --chip esp32 erase_flash` y `esptool --chip esp32 write_flash -z 0x1000 <fichero>.bin`.
2. Copiar `firmware/esp32/config.py` rellenándolo (WiFi, `API_URL` con la IP del ordenador, `API_KEY`, ids de sensor) y volcar:
   `mpremote cp firmware/esp32/config.py :config.py` · `mpremote cp firmware/esp32/main.py :main.py` · `mpremote reset`.
3. Ver lo que hace: `mpremote repl`.
4. La clave del sector sale de `claves_demo.json` (tras `python -m agrotechEFA2026.db.seed`). No la subas a git.

## Calibrar el suelo (obligatorio, sin esto el dato no vale)
1. Sensor **al aire**: anotar `suelo.read_u16()` en el REPL → `SUELO_AIRE` (= 0 %).
2. Sensor metido hasta la raya en un **vaso de agua**: → `SUELO_AGUA` (= 100 %).
3. Guardar los dos números en `config.py`. El firmware hace la media de 5 lecturas para filtrar picos.

## Si algo falla
- **El WiFi de clase bloquea el ESP32:** usar el punto de acceso del móvil (cambiar `WIFI_SSID`/`WIFI_PASS`). El firmware guarda hasta 200 lecturas y las envía al volver.
- **Demo sin hardware:** `python scripts/esp32_virtual.py --url http://localhost:8000 --clave <api_key> --corte 3` (simula el corte de WiFi).
- **Prueba de la demo:** mojar la tierra de la maceta; la humedad del suelo debe subir en pantalla en menos de 1 min.
