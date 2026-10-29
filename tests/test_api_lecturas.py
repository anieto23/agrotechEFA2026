from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from agrotechEFA2026.api import api
from agrotechEFA2026.db.consultas import generar_clave_sector
from agrotechEFA2026.db.models import Alert, Crop, CropRange, SensorData

SUELO = 3  # humedad del suelo del invernadero, umbral bajo 40 %
TEMPERATURA = 1


@pytest.fixture
def cliente():
    return TestClient(api)


def _enviar(cliente, claves, sensor_id=SUELO, clave=None, **cuerpo):
    cuerpo.setdefault("value", 55.0)
    cabeceras = {"X-API-Key": claves[str(sensor_id)] if clave is None else clave}
    return cliente.post(f"/api/sensors/{sensor_id}/data", json=cuerpo, headers=cabeceras)


def test_guarda_la_lectura_del_simulador(cliente, claves, motor):
    # Mismo formato que envía scripts/gen_sample_data.py
    cuerpo = {"sensor_id": SUELO, "timestamp": "2026-10-26T13:34:56+01:00", "type": "soil_moisture",
              "value": 55.0, "unit": "%"}
    r = _enviar(cliente, claves, **cuerpo)
    assert r.status_code == 201, r.text
    assert r.json()["alert"] is None
    assert r.json()["timestamp"].startswith("2026-10-26T12:34:56")  # pasada a UTC
    with Session(motor) as s:
        assert s.exec(select(SensorData)).one().value == 55.0


def test_lectura_baja_crea_alerta_una_sola_vez(cliente, claves, motor):
    primera = _enviar(cliente, claves, value=31.5).json()["alert"]
    assert primera["type"] == "LOW"
    assert primera["message"] == "Humedad del suelo 31.5 %, por debajo de lo recomendado (mínimo 40 %)"
    assert _enviar(cliente, claves, value=30.0).json()["alert"]["type"] == "LOW"
    with Session(motor) as s:
        assert len(s.exec(select(Alert)).all()) == 1  # no se repite mientras no se lea


def test_alerta_alta_con_rango_completo(cliente, claves, motor):
    with Session(motor) as s:
        tomate = s.exec(select(Crop).where(Crop.name == "tomate")).one()
        # Rango de prueba, no es un dato agronómico
        s.add(CropRange(crop_id=tomate.id, type="temperature", optimal_min=15, optimal_max=30, source="test"))
        s.commit()
    alerta = _enviar(cliente, claves, sensor_id=TEMPERATURA, value=35.0).json()["alert"]
    assert alerta == {"type": "HIGH", "message": "Temperatura 35 ºC, por encima de lo recomendado (15-30 ºC)"}


def test_sin_fecha_usa_la_hora_actual(cliente, claves):
    r = _enviar(cliente, claves)
    hora = datetime.fromisoformat(r.json()["timestamp"].replace("Z", "+00:00"))
    assert abs(datetime.now(timezone.utc) - hora) < timedelta(minutes=1)


@pytest.mark.parametrize(
    "cambios, codigo",
    [
        ({"clave": "falsa"}, 401),
        ({"clave": ""}, 401),
        ({"sensor_id": 999, "clave": "x"}, 404),
        ({"value": 150.0}, 422),  # humedad por encima del 100 %
        ({"value": "mucha"}, 422),
        ({"type": "temperature"}, 422),  # el sensor 3 mide humedad del suelo
        ({"unit": "ºC"}, 422),
        ({"timestamp": "2099-01-01T00:00:00Z"}, 422),
        ({"timestamp": "ayer"}, 422),
    ],
)
def test_rechaza_lecturas_malas(cliente, claves, motor, cambios, codigo):
    r = _enviar(cliente, claves, **cambios)
    assert r.status_code == codigo
    assert isinstance(r.json()["detail"], str)  # siempre un texto, como pide el contrato
    with Session(motor) as s:
        assert s.exec(select(SensorData)).all() == []


def test_clave_de_otra_parcela_no_vale(cliente, claves):
    # La clave del sensor 5 es de la parcela «Aguacates», no del invernadero
    assert _enviar(cliente, claves, clave=claves["5"]).status_code == 401


def test_clave_nueva_del_sector_sustituye_a_la_vieja(cliente, claves):
    nueva = generar_clave_sector(1, 1)  # agricultor, sector del invernadero
    assert _enviar(cliente, claves, clave=nueva).status_code == 201
    assert _enviar(cliente, claves).status_code == 401  # la del seed ya no vale


def test_sensor_id_del_cuerpo_distinto_al_de_la_direccion(cliente, claves):
    r = cliente.post(f"/api/sensors/{SUELO}/data", json={"sensor_id": TEMPERATURA, "value": 20},
                     headers={"X-API-Key": claves[str(SUELO)]})
    assert r.status_code == 422
