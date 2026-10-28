from datetime import timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, select

from agrotechEFA2026.db import seed
from agrotechEFA2026.db.models import (
    ACCIONES_POR_TIPO,
    TIPOS_MEDIDA,
    Crop,
    CropRange,
    Parcel,
    ParcelViewer,
    Sector,
    Sensor,
    User,
)
from agrotechEFA2026.db.seguridad import hash_api_key, hash_password, verificar_password
from agrotechEFA2026.db.session import crear_motor, crear_tablas
from scripts import gen_sample_data as simulador

PASSWORDS = {"farmer": "prueba-agricultor", "technician": "prueba-tecnico"}


@pytest.fixture
def s():
    motor = crear_motor("sqlite://")  # base de datos en memoria, nueva en cada test
    crear_tablas(motor)
    with Session(motor) as sesion:
        yield sesion
    SQLModel.metadata.drop_all(motor)


@pytest.fixture
def claves(s):
    return seed.sembrar(s, PASSWORDS)


def test_password_hash_y_verificacion():
    guardado = hash_password("secreta")
    assert "secreta" not in guardado
    assert verificar_password("secreta", guardado)
    assert not verificar_password("otra", guardado)
    assert hash_password("secreta") != guardado  # cada hash lleva su propia sal


def test_verificar_password_con_formato_roto():
    assert not verificar_password("x", "")
    assert not verificar_password("x", "md5$1$aa$bb")


def test_seed_crea_lo_del_contrato(s, claves):
    assert len(s.exec(select(User)).all()) == 2
    assert len(s.exec(select(Parcel)).all()) == 3
    assert len(s.exec(select(Sector)).all()) == 3
    assert len(s.exec(select(Sensor)).all()) == 12
    assert len(s.exec(select(ParcelViewer)).all()) == 3
    assert {c.name for c in s.exec(select(Crop))} == set(seed.CULTIVOS_DEMO)
    # No hay óptimos inventados: se rellenan cuando haya fuentes
    assert s.exec(select(CropRange)).all() == []


def test_seed_no_guarda_secretos_en_claro(s, claves):
    for usuario in s.exec(select(User)):
        assert verificar_password(PASSWORDS[usuario.role], usuario.password_hash)
        assert PASSWORDS[usuario.role] not in usuario.password_hash
    for sensor in s.exec(select(Sensor)):
        assert sensor.sector.api_key_hash == hash_api_key(claves[str(sensor.id)])


def test_ids_de_sensores_coinciden_con_el_simulador(s, claves):
    assert sorted(claves, key=int) == [str(i) for i in range(1, 13)]
    for p in simulador.PARCELAS:
        for tipo in TIPOS_MEDIDA:
            sensor = s.get(Sensor, simulador.sensor_id(p, tipo))
            assert sensor.type == tipo
            assert sensor.sector.parcel.name == p.nombre


def test_tipos_de_medida_iguales_que_el_simulador():
    assert TIPOS_MEDIDA == simulador.TIPOS


def test_cada_parcela_de_ejemplo_tiene_un_sector_entero(s, claves):
    for sector in s.exec(select(Sector)):
        assert (sector.left_pct, sector.top_pct, sector.width_pct, sector.height_pct) == (0, 0, 100, 100)
        assert sector.crop_id is not None


def test_un_solo_sensor_de_cada_tipo_por_sector(s, claves):
    s.add(Sensor(sector_id=1, type="temperature", unit="ºC"))
    with pytest.raises(IntegrityError):
        s.commit()


def test_exterior_no_permite_controlar_temperatura():
    assert "heating" not in ACCIONES_POR_TIPO["outdoor"]
    assert "ventilation" not in ACCIONES_POR_TIPO["outdoor"]
    assert set(ACCIONES_POR_TIPO["outdoor"]) <= set(ACCIONES_POR_TIPO["indoor"])


def test_fechas_se_leen_en_utc(s, claves):
    usuario = s.exec(select(User)).first()
    s.expire_all()  # obliga a leerlo otra vez de la base de datos
    assert s.get(User, usuario.id).created_at.utcoffset() == timedelta(0)


def test_nombre_de_usuario_unico(s, claves):
    s.add(User(username="agricultor", password_hash="x"))
    with pytest.raises(IntegrityError):
        s.commit()
