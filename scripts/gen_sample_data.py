"""Simulador de sensores de Agrotech.

Genera lecturas realistas (temperatura, humedad del aire, humedad del suelo, luz)
de 3 parcelas de la Costa Tropical y las imprime, las guarda o las envía a la API.

Ejemplos:
    python scripts/gen_sample_data.py                          # imprime en directo cada 5 s
    python scripts/gen_sample_data.py --historico 14 --salida datos.jsonl
    python scripts/gen_sample_data.py --url http://localhost:8000 --rapido
    python scripts/gen_sample_data.py --evento sequia          # fuerza una alerta de humedad
"""
import argparse
import json
import math
import random
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta

# Tipos del contrato: (tipo, unidad, mínimo válido, máximo válido)
TIPOS = {
    "temperature": ("ºC", -10.0, 50.0),
    "air_humidity": ("%", 0.0, 100.0),
    "soil_moisture": ("%", 0.0, 100.0),
    "light": ("lx", 0.0, 120000.0),
}
# Temperatura media mensual en Motril (ene..dic)
TEMP_MES = [12.5, 13.0, 14.5, 16.0, 19.0, 22.5, 25.5, 26.5, 24.0, 20.0, 16.0, 13.5]


@dataclass
class Parcela:
    id: int
    nombre: str
    cultivo: str
    umbral_suelo: float  # por debajo de esto el sensor debería avisar
    dt_temp: float = 0.0  # grados extra (invernadero)
    amp: float = 5.0  # oscilación diaria de temperatura
    luz: float = 1.0  # factor de luz (invernadero filtra)


PARCELAS = [
    Parcela(1, "Invernadero tomates", "tomate", 40.0, dt_temp=4.0, amp=8.0, luz=0.7),
    Parcela(2, "Aguacates", "aguacate", 35.0),
    Parcela(3, "Mangos", "mango", 30.0),
]


def sensor_id(parcela: Parcela, tipo: str) -> int:
    # shortcut: ids provisionales (4 por parcela), cambiar cuando A fije los ids reales en el contrato
    return (parcela.id - 1) * 4 + list(TIPOS).index(tipo) + 1


class Simulador:
    """Estado de una parcela. El suelo depende de su historia, por eso hay que avanzarlo en orden."""

    def __init__(self, parcela: Parcela, rng: random.Random, sequia: bool = False):
        self.p = parcela
        self.rng = rng
        self.sequia = sequia
        self.suelo = parcela.umbral_suelo + 8 if sequia else 62.0
        self.dia = None
        self.nubes = 1.0  # 1 = despejado
        self.llueve = False
        self.ultimo = None

    def _nuevo_dia(self, t: datetime) -> None:
        self.dia = t.date()
        self.llueve = self.rng.random() < 0.06
        self.nubes = 0.25 if self.llueve else self.rng.uniform(0.5, 1.0)
        if self.llueve and not self.sequia:
            self.suelo = min(95.0, self.suelo + 15)

    def _temperatura(self, t: datetime) -> float:
        h = t.hour + t.minute / 60
        media = TEMP_MES[t.month - 1] + self.p.dt_temp
        return media + self.p.amp * math.sin(2 * math.pi * (h - 9) / 24)  # pico a las 15:00

    def _luz(self, t: datetime) -> float:
        doy = t.timetuple().tm_yday
        estacion = math.sin(2 * math.pi * (doy - 80) / 365)  # -1 invierno, +1 verano
        duracion = 12 + 2.5 * estacion
        h = t.hour + t.minute / 60 - (13.0 - duracion / 2)
        if not 0 < h < duracion:
            return 0.0
        pico = (70000 + 30000 * estacion) * self.p.luz
        return pico * math.sin(math.pi * h / duracion) * self.nubes

    def lecturas(self, t: datetime) -> dict:
        """Avanza el estado hasta `t` y devuelve {tipo: valor}."""
        if self.dia != t.date():
            self._nuevo_dia(t)
        temp = self._temperatura(t) + self.rng.gauss(0, 0.3)
        if self.ultimo is not None:
            horas = (t - self.ultimo).total_seconds() / 3600
            ritmo = 0.25 * (1 + max(0.0, temp - 18) * 0.06) * (6 if self.sequia else 1)
            self.suelo = max(0.0, self.suelo - ritmo * horas)
            # riego automático a las 7:00 si el suelo está cerca del mínimo
            if (not self.sequia and self.ultimo.hour < 7 <= t.hour
                    and self.suelo < self.p.umbral_suelo + 10):
                self.suelo = min(75.0, self.suelo + 30)
        self.ultimo = t
        aire = 95 - 2.0 * (temp - 10) + self.rng.gauss(0, 1.5) + (15 if self.llueve else 0)
        luz = self._luz(t) * self.rng.uniform(0.97, 1.03)
        return {
            "temperature": round(temp, 1),
            "air_humidity": round(aire, 1),
            "soil_moisture": round(self.suelo + self.rng.gauss(0, 0.2), 1),
            "light": round(luz),
        }


def a_payloads(parcela: Parcela, t: datetime, valores: dict) -> list:
    """Convierte las lecturas al JSON del contrato, recortando a rango válido."""
    out = []
    for tipo, valor in valores.items():
        unidad, minimo, maximo = TIPOS[tipo]
        out.append({
            "sensor_id": sensor_id(parcela, tipo),
            "timestamp": t.isoformat(timespec="seconds"),
            "type": tipo,
            "value": min(max(valor, minimo), maximo),
            "unit": unidad,
        })
    return out


def historico(dias: int, paso_min: int, semilla: int, ahora: datetime):
    """Genera `dias` de historia hasta `ahora`, en orden cronológico."""
    sims = [Simulador(p, random.Random(semilla + p.id)) for p in PARCELAS]
    t = ahora - timedelta(days=dias)
    while t <= ahora:
        for sim in sims:
            yield from a_payloads(sim.p, t, sim.lecturas(t))
        t += timedelta(minutes=paso_min)


class Salida:
    """Destino de las lecturas: pantalla, fichero JSON-lines o API REST."""

    def __init__(self, url=None, claves=None, fichero=None):
        self.url, self.claves = url, claves or {}
        self.f = open(fichero, "w", encoding="utf-8") if fichero else None
        self.avisado = False

    def enviar(self, lectura: dict) -> None:
        if self.f:
            self.f.write(json.dumps(lectura, ensure_ascii=False) + "\n")
        elif not self.url:
            print(json.dumps(lectura, ensure_ascii=False), flush=True)
        else:
            self._post(lectura)

    def _post(self, lectura: dict) -> None:
        sid = str(lectura["sensor_id"])
        req = urllib.request.Request(
            f"{self.url.rstrip('/')}/api/sensors/{sid}/data",
            data=json.dumps(lectura).encode(),
            headers={"Content-Type": "application/json", "X-API-Key": self.claves.get(sid, "")},
        )
        try:
            urllib.request.urlopen(req, timeout=5).close()
        except (urllib.error.URLError, OSError) as e:
            if not self.avisado:  # un solo aviso: la demo no debe caerse si la API tarda
                print(f"[aviso] no se pudo enviar: {e}", file=sys.stderr)
                self.avisado = True

    def cerrar(self) -> None:
        if self.f:
            self.f.close()


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", help="API a la que enviar (si no, imprime por pantalla)")
    ap.add_argument("--claves", help="JSON {sensor_id: api_key} para la cabecera X-API-Key")
    ap.add_argument("--salida", help="guardar en un fichero .jsonl en vez de enviar")
    ap.add_argument("--intervalo", type=float, default=5.0, help="segundos entre lecturas (def. 5)")
    ap.add_argument("--rapido", action="store_true", help="un día simulado cada 2 minutos")
    ap.add_argument("--historico", type=int, metavar="DIAS", help="genera DIAS de historia y termina")
    ap.add_argument("--paso", type=int, default=15, help="minutos entre lecturas del histórico (def. 15)")
    ap.add_argument("--parcelas", type=int, default=len(PARCELAS), help="nº de parcelas (1-3)")
    ap.add_argument("--evento", choices=["sequia"], help="fuerza una situación para probar alertas")
    ap.add_argument("--semilla", type=int, default=42, help="misma semilla = mismos datos")
    a = ap.parse_args(argv)

    claves = json.load(open(a.claves, encoding="utf-8")) if a.claves else {}
    salida = Salida(a.url, claves, a.salida)
    ahora = datetime.now().astimezone()
    try:
        if a.historico:
            n = 0
            for lectura in historico(a.historico, a.paso, a.semilla, ahora):
                salida.enviar(lectura)
                n += 1
            print(f"{n} lecturas generadas", file=sys.stderr)
            return
        sims = [Simulador(p, random.Random(a.semilla + p.id), a.evento == "sequia")
                for p in PARCELAS[:a.parcelas]]
        velocidad = 720 if a.rapido else 1  # segundos simulados por segundo real
        t = ahora
        while True:
            for sim in sims:
                for lectura in a_payloads(sim.p, t, sim.lecturas(t)):
                    salida.enviar(lectura)
            time.sleep(a.intervalo)
            t += timedelta(seconds=a.intervalo * velocidad)
    except KeyboardInterrupt:
        pass
    finally:
        salida.cerrar()


if __name__ == "__main__":
    main()
