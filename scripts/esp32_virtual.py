"""ESP32 virtual (plan B): se comporta como firmware/esp32/main.py sin hardware.

Manda las 4 lecturas de un sector cada N segundos con su X-API-Key. Si la API no responde
las guarda y las reenvía al volver (como el firmware). `--corte 3` simula un corte de WiFi
tras 3 envíos para enseñar ese comportamiento.

    python scripts/esp32_virtual.py --url http://localhost:8000 --clave <api_key> --parcela 1
"""
import argparse
import json
import random
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

try:  # como módulo (tests) o ejecutado como script
    from scripts.gen_sample_data import PARCELAS, Simulador, a_payloads
except ModuleNotFoundError:
    from gen_sample_data import PARCELAS, Simulador, a_payloads

MAX_PENDIENTES = 200


def enviar(url: str, clave: str, lectura: dict) -> bool:
    req = urllib.request.Request(
        f"{url.rstrip('/')}/api/sensors/{lectura['sensor_id']}/data",
        data=json.dumps(lectura).encode(),
        headers={"Content-Type": "application/json", "X-API-Key": clave},
    )
    try:
        urllib.request.urlopen(req, timeout=5).close()
        return True
    except urllib.error.HTTPError as e:
        return e.code == 422  # dato inválido: reenviarlo no lo arregla
    except OSError:
        return False


def volcar(url: str, clave: str, pendientes: list) -> None:
    """Envía en orden; para al primer fallo y conserva el resto."""
    while pendientes and enviar(url, clave, pendientes[0]):
        pendientes.pop(0)
    del pendientes[:-MAX_PENDIENTES]


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://localhost:8000")
    ap.add_argument("--clave", required=True, help="X-API-Key del sector")
    ap.add_argument("--parcela", type=int, default=1, choices=[p.id for p in PARCELAS])
    ap.add_argument("--intervalo", type=float, default=30.0)
    ap.add_argument("--corte", type=int, metavar="N", help="simula corte de WiFi tras N envíos")
    a = ap.parse_args(argv)

    sim = Simulador(next(p for p in PARCELAS if p.id == a.parcela), random.Random())
    pendientes, ciclos = [], 0
    try:
        while True:
            ciclos += 1
            pendientes += a_payloads(sim.p, datetime.now(timezone.utc), sim.lecturas(datetime.now(timezone.utc)))
            if a.corte and a.corte < ciclos <= a.corte + 3:
                print(f"[corte WiFi] {len(pendientes)} lecturas guardadas")
            else:
                volcar(a.url, a.clave, pendientes)
                print(f"enviado; pendientes: {len(pendientes)}")
            time.sleep(a.intervalo)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
