# Estado de D (28-oct-2026) – qué hay hecho y cómo usarlo

Todo probado con la base de datos nueva (sectores). 112 tests en verde.

| Tarea | Archivo | Estado |
|---|---|---|
| D1 Simulador | `scripts/gen_sample_data.py` | Hecho. Envía a la API con `--url` y `--claves claves_demo.json`; `--historico`, `--rapido`, `--evento sequia` |
| D2 ESP32 | `firmware/esp32/`, `docs/hardware.md` | Código escrito, **sin probar en hardware real** (faltan las piezas) |
| D2 plan B | `scripts/esp32_virtual.py` | Hecho. Se comporta como el firmware, con corte de WiFi simulado (`--corte 3`) |
| D3 Riego | `agrotechEFA2026/services/riego.py`, `data/cultivos.json` | Hecho. Cifras de cultivos **pendientes de validar** con el profesorado agrario |
| D4 Telegram | `agrotechEFA2026/services/telegram.py` | Hecho. Token y chat id en `.env` (nunca en git) |
| D5 Exportar | `agrotechEFA2026/services/export.py` | CSV y PDF hechos. **Falta el botón** en el panel |
| D5 Despliegue | `Dockerfile` | Escrito, **sin probar** |

## Para B (panel)
```python
from agrotechEFA2026.services import riego, export
rec = riego.recomendar(usuario_id, parcela_id)
# {"regar": bool, "minutos": int, "motivo": "texto listo para la tarjeta", "confianza": "alta|media|baja"}
csv_texto = export.historico_csv(usuario_id, parcela_id, desde, hasta)   # str
pdf_bytes = export.informe_pdf(usuario_id, parcela_id, desde, hasta, rec["motivo"])  # bytes
```
`recomendar` lanza `ValueError` si la parcela no tiene cultivo con datos en `data/cultivos.json` (tomate, aguacate, mango, chirimoya).

## Para C (alertas)
```python
from agrotechEFA2026.services import telegram
telegram.avisar("⚠️ Parcela 2: humedad del suelo 22 % (mínimo 35 %)", clave=f"sensor-{sensor_id}")
```
Devuelve `True` si se envió; `False` si ya hubo un aviso con esa `clave` en los últimos 30 min o no hay token. Nunca lanza excepción.

## Para A
Esta rama toca `pyproject.toml` y `requirements.txt` (añade `fpdf2`, para el PDF). Nada más de lo vuestro.
