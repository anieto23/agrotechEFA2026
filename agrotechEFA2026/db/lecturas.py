"""Entrada de lecturas desde los aparatos o el simulador (ver docs/contrato.md).

La API llama a `guardar_lectura`; aquí no hay nada de HTTP para poder probarlo sin servidor.
"""
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlmodel import Session, select

from .consultas import evaluar_estado, limites_sensor
from .models import TIPOS_MEDIDA, Alert, Sector, Sensor, SensorData
from .seguridad import hash_api_key
from .session import sesion

NOMBRES_MEDIDA = {
    "temperature": "Temperatura",
    "air_humidity": "Humedad del aire",
    "soil_moisture": "Humedad del suelo",
    "light": "Luz",
}
# Margen para relojes un poco adelantados; más allá es un error del aparato
MARGEN_FUTURO = timedelta(minutes=5)


class ClaveIncorrecta(Exception):
    """La clave del aparato no es la del sector del sensor (HTTP 401)."""


class NoEncontrado(Exception):
    """El sensor no existe o está desactivado (HTTP 404)."""


@dataclass
class Resultado:
    lectura: SensorData
    alerta: Optional[Alert]


def _mensaje_alerta(sensor: Sensor, valor: float, minimo: Optional[float], maximo: Optional[float]) -> str:
    nombre = NOMBRES_MEDIDA.get(sensor.type, sensor.type)
    if minimo is not None and valor < minimo:
        limite = f"{minimo:g}-{maximo:g}" if maximo is not None else f"mínimo {minimo:g}"
        return f"{nombre} {valor:g} {sensor.unit}, por debajo de lo recomendado ({limite} {sensor.unit})"
    limite = f"{minimo:g}-{maximo:g}" if minimo is not None else f"máximo {maximo:g}"
    return f"{nombre} {valor:g} {sensor.unit}, por encima de lo recomendado ({limite} {sensor.unit})"


def _alerta_si_hace_falta(s: Session, sensor: Sensor, sector: Sector, lectura: SensorData) -> Optional[Alert]:
    """Crea una alerta si la lectura sale del rango, salvo que ya haya una igual sin leer."""
    minimo, maximo = limites_sensor(s, sensor, sector)
    estado = evaluar_estado(lectura.value, minimo, maximo)
    if estado not in ("low", "high"):
        return None
    tipo = "LOW" if estado == "low" else "HIGH"
    pendiente = s.exec(
        select(Alert).where(Alert.sensor_id == sensor.id, Alert.type == tipo, Alert.acknowledged == False)  # noqa: E712
    ).first()
    if pendiente:  # no repetir el mismo aviso con cada lectura
        return pendiente
    alerta = Alert(
        sensor_id=sensor.id,
        timestamp=lectura.timestamp,
        type=tipo,
        message=_mensaje_alerta(sensor, lectura.value, minimo, maximo),
    )
    s.add(alerta)
    return alerta


def guardar_lectura(
    sensor_id: int,
    clave: str,
    valor: float,
    timestamp: Optional[datetime] = None,
    tipo: Optional[str] = None,
    unidad: Optional[str] = None,
) -> Resultado:
    """Valida y guarda una lectura. `tipo` y `unidad`, si llegan, deben coincidir con el sensor."""
    with sesion() as s:
        sensor = s.get(Sensor, sensor_id)
        sector = s.get(Sector, sensor.sector_id) if sensor else None
        if sensor is None or not sensor.active or not sector.active:
            raise NoEncontrado("El sensor no existe o está desactivado.")
        if not clave or hash_api_key(clave) != sector.api_key_hash:
            raise ClaveIncorrecta("Clave del aparato incorrecta.")

        if tipo is not None and tipo != sensor.type:
            raise ValueError(f"Este sensor mide {sensor.type}, no {tipo}.")
        if unidad is not None and unidad != sensor.unit:
            raise ValueError(f"La unidad de este sensor es {sensor.unit}, no {unidad}.")
        _, minimo, maximo = TIPOS_MEDIDA[sensor.type]
        if not math.isfinite(valor) or not minimo <= valor <= maximo:
            raise ValueError(f"Valor fuera de rango: {sensor.type} debe estar entre {minimo:g} y {maximo:g} {sensor.unit}.")

        ahora = datetime.now(timezone.utc)
        if timestamp is None:
            timestamp = ahora
        elif timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)  # sin zona horaria se entiende UTC
        if timestamp > ahora + MARGEN_FUTURO:
            raise ValueError("La fecha de la lectura está en el futuro: revisa el reloj del aparato.")

        lectura = SensorData(sensor_id=sensor.id, timestamp=timestamp.astimezone(timezone.utc), value=float(valor))
        s.add(lectura)
        alerta = _alerta_si_hace_falta(s, sensor, sector, lectura)
        s.commit()
        return Resultado(lectura, alerta)
