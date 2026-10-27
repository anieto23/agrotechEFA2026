"""Recomendación de riego: reglas simples que el jurado puede entender.

    recomendar(usuario_id, parcela_id) -> {"regar", "minutos", "motivo", "confianza"}

1. Humedad media del suelo de las últimas 3 h por debajo del umbral del cultivo -> regar.
2. Minutos = déficit hasta el objetivo x minutos por punto del cultivo (+20 % si hace calor).
3. Si Open-Meteo prevé más de 2 mm de lluvia en 24 h -> no regar, lloverá.
Si Open-Meteo falla se usa la última previsión guardada (confianza media).
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Optional

import requests
from sqlmodel import select

from ..db import consultas
from ..db.models import Crop, Node
from ..db.session import sesion

RAIZ = Path(__file__).resolve().parents[2]
CULTIVOS = RAIZ / "data" / "cultivos.json"
CACHE_PREVISION = RAIZ / "data" / "prevision.json"
LLUVIA_MINIMA_MM = 2.0
CALOR_C = 30.0
VENTANA_H = 3
# Motril; si la parcela tiene lat/lon se podría usar la suya
LAT, LON = 36.75, -3.52
URL_METEO = "https://api.open-meteo.com/v1/forecast"


def cargar_cultivos() -> dict:
    datos = json.loads(CULTIVOS.read_text(encoding="utf-8"))
    return {k: v for k, v in datos.items() if not k.startswith("_")}


def obtener_prevision(lat: float = LAT, lon: float = LON) -> Optional[dict]:
    """{"lluvia_mm", "tmax", "en_vivo"} de las próximas 24 h, o None si no hay ni caché."""
    try:
        r = requests.get(URL_METEO, timeout=5, params={
            "latitude": lat, "longitude": lon, "forecast_days": 1,
            "daily": "precipitation_sum,temperature_2m_max", "timezone": "Europe/Madrid",
        })
        r.raise_for_status()
        diario = r.json()["daily"]
        prevision = {"lluvia_mm": diario["precipitation_sum"][0] or 0.0, "tmax": diario["temperature_2m_max"][0]}
        CACHE_PREVISION.write_text(json.dumps(prevision), encoding="utf-8")
        return {**prevision, "en_vivo": True}
    except (requests.RequestException, KeyError, IndexError, ValueError):
        try:
            return {**json.loads(CACHE_PREVISION.read_text(encoding="utf-8")), "en_vivo": False}
        except (OSError, ValueError):
            return None


def decidir(humedad: Optional[float], cultivo: dict, prevision: Optional[dict]) -> dict:
    """Parte pura de la recomendación (sin base de datos ni red), para poder probarla."""
    if humedad is None:
        return {"regar": False, "minutos": 0, "confianza": "baja",
                "motivo": f"Sin lecturas de humedad del suelo en las últimas {VENTANA_H} h: no se puede recomendar."}
    umbral, objetivo = cultivo["umbral_suelo"], cultivo["objetivo_suelo"]
    lluvia = prevision["lluvia_mm"] if prevision else 0.0
    tmax = prevision["tmax"] if prevision else None
    confianza = "alta" if prevision and prevision["en_vivo"] else "media"
    clima = f", {tmax:.0f} ºC" if tmax is not None else ""
    if humedad >= umbral:
        return {"regar": False, "minutos": 0, "confianza": confianza,
                "motivo": f"No regar: suelo al {humedad:.0f} % (mínimo {umbral} %){clima}."}
    if lluvia > LLUVIA_MINIMA_MM:
        return {"regar": False, "minutos": 0, "confianza": confianza,
                "motivo": f"No regar, lloverá: {lluvia:.1f} mm previstos en 24 h (suelo al {humedad:.0f} %, mínimo {umbral} %)."}
    factor = 1.2 if tmax is not None and tmax >= CALOR_C else 1.0
    minutos = max(1, round((objetivo - humedad) * cultivo["min_por_punto"] * factor))
    lluvia_txt = "sin lluvia prevista" if prevision else "sin previsión del tiempo"
    return {"regar": True, "minutos": minutos, "confianza": confianza,
            "motivo": f"Regar {minutos} min hoy antes de las 8:00: suelo al {humedad:.0f} % (mínimo {umbral} %){clima}, {lluvia_txt}."}


def _cultivo_y_sensores(usuario_id: int, parcela_id: int) -> tuple[Optional[str], list[int]]:
    """Cultivo del primer nodo con cultivo y ids de sus sensores de humedad del suelo."""
    estados = consultas.ultimas_lecturas(usuario_id, parcela_id)  # comprueba permisos
    suelo = [e.sensor_id for e in estados if e.type == "soil_moisture"]
    with sesion() as s:
        nombre = s.exec(
            select(Crop.name).join(Node, Node.crop_id == Crop.id).where(Node.parcel_id == parcela_id)
        ).first()
    return nombre, suelo


def recomendar(usuario_id: int, parcela_id: int, ahora: Optional[datetime] = None) -> dict:
    nombre, sensores = _cultivo_y_sensores(usuario_id, parcela_id)
    cultivos = cargar_cultivos()
    if nombre not in cultivos:
        raise ValueError("La parcela no tiene un cultivo con datos de riego (ver data/cultivos.json).")
    ahora = ahora or datetime.now(timezone.utc)
    valores = [
        d.value
        for sid in sensores
        for d in consultas.historico(usuario_id, sid, ahora - timedelta(hours=VENTANA_H), ahora)
    ]
    return decidir(mean(valores) if valores else None, cultivos[nombre], obtener_prevision())
