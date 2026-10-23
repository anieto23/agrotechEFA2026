"""Vigila las lecturas y avisa por Telegram si un valor sale de su umbral.

Lee líneas JSON (formato del contrato) de un fichero que el simulador va rellenando:
    {"sensor_id": 2, "timestamp": "...", "type": "soil_moisture", "value": 18.0, "unit": "%"}

Uso:  python scripts/vigilante.py [--fichero data/lecturas.jsonl] [--seco]   (--seco = no envía, solo imprime)
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

from scripts.telegram_prueba import cargar_env, llamar

# shortcut: umbrales por tipo, no por sensor; pasar a sensors.umbral_min/max cuando exista la BBDD de A.
UMBRALES = {
    "temperature": (5, 35),
    "soil_moisture": (25, 80),
    "air_humidity": (30, 90),
}
ENFRIAMIENTO = 30 * 60  # máx. 1 aviso por sensor cada 30 min


def fuera_de_rango(lectura):
    """Devuelve el texto del aviso si la lectura sale de su umbral, o None."""
    minimo, maximo = UMBRALES.get(lectura["type"], (None, None))
    v = lectura["value"]
    if minimo is not None and v < minimo:
        return f"{lectura['type']} baja: {v}{lectura['unit']} (mínimo {minimo})"
    if maximo is not None and v > maximo:
        return f"{lectura['type']} alta: {v}{lectura['unit']} (máximo {maximo})"
    return None


def decidir(lectura, ultimo_aviso, ahora):
    """Texto a enviar o None. Actualiza ultimo_aviso (sensor_id -> instante)."""
    texto = fuera_de_rango(lectura)
    sid = lectura["sensor_id"]
    if texto is None:
        ultimo_aviso.pop(sid, None)  # volvió a rango: el próximo fallo avisa de inmediato
        return None
    if ahora - ultimo_aviso.get(sid, -ENFRIAMIENTO) < ENFRIAMIENTO:
        return None
    ultimo_aviso[sid] = ahora
    return f"⚠️ Agrotech, sensor {sid}: {texto}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fichero", default="data/lecturas.jsonl")
    ap.add_argument("--seco", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows (cp1252) no imprime emojis
    cargar_env()
    token, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not args.seco and not (token and chat):
        raise SystemExit("Faltan TELEGRAM_TOKEN / TELEGRAM_CHAT_ID en .env (o usa --seco)")

    ruta, ultimo_aviso, posicion = Path(args.fichero), {}, 0
    while True:
        if ruta.exists():
            with ruta.open(encoding="utf-8") as f:
                f.seek(posicion)
                for linea in f:
                    if not linea.endswith("\n"):
                        break  # línea a medio escribir: se lee en la siguiente vuelta
                    posicion += len(linea.encode("utf-8"))
                    try:
                        texto = decidir(json.loads(linea), ultimo_aviso, time.time())
                    except (ValueError, KeyError):
                        continue  # línea mal formada: se ignora
                    if texto:
                        print(texto)
                        if not args.seco:
                            llamar(token, "sendMessage", chat_id=chat, text=texto)
        time.sleep(2)


if __name__ == "__main__":
    main()
