from datetime import datetime, timedelta, timezone

import pytest
from sqlmodel import Session, select

from agrotechEFA2026.db import consultas as c
from agrotechEFA2026.db.models import Alert, Crop, CropRange, Parcel, SensorData, User
from agrotechEFA2026.db.seguridad import hash_password

AHORA = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)
AGRICULTOR, TECNICO = 1, 2  # ids que crea el seed
INVERNADERO, AGUACATES = 1, 2  # parcelas del seed
SUELO_INVERNADERO = 3  # sensor soil_moisture de la parcela 1 (umbral bajo 40 %)


def _guardar(motor, *objetos):
    with Session(motor) as s:
        s.add_all(objetos)
        s.commit()


def _cultivo(motor, nombre: str) -> int:
    with Session(motor) as s:
        return s.exec(select(Crop.id).where(Crop.name == nombre)).one()


def _otro_agricultor(motor) -> int:
    with Session(motor) as s:
        otro = User(username="vecino", role="farmer", password_hash=hash_password("x"))
        s.add(otro)
        s.commit()
        return otro.id


# ---------- evaluar_estado ----------

@pytest.mark.parametrize(
    "valor, minimo, maximo, esperado",
    [
        (None, 10, 20, "no_data"),
        (15, None, None, "no_range"),
        (5, 10, 20, "low"),
        (25, 10, 20, "high"),
        (10, 10, 20, "ok"),  # los límites cuentan como dentro
        (20, 10, 20, "ok"),
        (5, 10, None, "low"),  # solo umbral bajo
        (99, 10, None, "ok"),
    ],
)
def test_evaluar_estado(valor, minimo, maximo, esperado):
    assert c.evaluar_estado(valor, minimo, maximo) == esperado


# ---------- Parcelas y permisos ----------

def test_agricultor_y_tecnico_ven_las_3_parcelas(motor):
    assert [p.name for p in c.listar_parcelas(AGRICULTOR)] == ["Aguacates", "Invernadero tomates", "Mangos"]
    assert len(c.listar_parcelas(TECNICO)) == 3  # las tiene compartidas


def test_nadie_ve_parcelas_ajenas(motor):
    vecino = _otro_agricultor(motor)
    assert c.listar_parcelas(vecino) == []
    assert c.obtener_parcela(vecino, INVERNADERO) is None
    with pytest.raises(PermissionError):
        c.ultimas_lecturas(vecino, INVERNADERO)


def test_usuario_inexistente(motor):
    with pytest.raises(PermissionError):
        c.listar_parcelas(999)


def test_crear_parcela(motor):
    p = c.crear_parcela(AGRICULTOR, "  Huerto  ", "outdoor", 10, 5)
    assert (p.name, p.kind, p.owner_id) == ("Huerto", "outdoor", AGRICULTOR)
    assert c.obtener_parcela(AGRICULTOR, p.id).width_m == 10


@pytest.mark.parametrize(
    "nombre, tipo, ancho, largo",
    [("", "outdoor", 10, 5), ("X", "garaje", 10, 5), ("X", "indoor", 0, 5), ("X", "indoor", 10, 99999)],
)
def test_crear_parcela_con_datos_malos(motor, nombre, tipo, ancho, largo):
    with pytest.raises(ValueError):
        c.crear_parcela(AGRICULTOR, nombre, tipo, ancho, largo)


def test_tecnico_no_crea_parcelas(motor):
    with pytest.raises(PermissionError):
        c.crear_parcela(TECNICO, "X", "indoor", 10, 5)


# ---------- Nodos y sensores ----------

def test_colocar_y_mover_nodo(motor):
    nodo, clave = c.colocar_nodo(AGRICULTOR, INVERNADERO, "Nodo norte", 5, 5, 2, cultivo_id=_cultivo(motor, "tomate"))
    assert len(clave) > 20 and clave not in nodo.api_key_hash
    assert c.mover_nodo(AGRICULTOR, nodo.id, 39, 24).pos_x_m == 39


def test_nodo_fuera_de_la_parcela(motor):
    # El invernadero mide 40 x 25 m
    with pytest.raises(ValueError, match="fuera de la parcela"):
        c.colocar_nodo(AGRICULTOR, INVERNADERO, "Nodo", 41, 5, 2)
    with pytest.raises(ValueError, match="fuera de la parcela"):
        c.mover_nodo(AGRICULTOR, 1, 5, -1)


def test_nodo_con_cultivo_inexistente(motor):
    with pytest.raises(ValueError, match="cultivo"):
        c.colocar_nodo(AGRICULTOR, INVERNADERO, "Nodo", 5, 5, 2, cultivo_id=999)


def test_tecnico_no_coloca_nodos(motor):
    with pytest.raises(PermissionError):
        c.colocar_nodo(TECNICO, INVERNADERO, "Nodo", 5, 5, 2)


def test_crear_sensor_y_validar_umbrales(motor):
    sensor = c.crear_sensor(AGRICULTOR, 1, "temperature", 15, 30)
    assert (sensor.unit, sensor.threshold_low) == ("ºC", 15)
    with pytest.raises(ValueError):
        c.crear_sensor(AGRICULTOR, 1, "ph")
    with pytest.raises(ValueError):
        c.crear_sensor(AGRICULTOR, 1, "temperature", 30, 15)  # bajo mayor que alto
    with pytest.raises(ValueError):
        c.crear_sensor(AGRICULTOR, 1, "air_humidity", None, 150)  # fuera de 0-100 %


# ---------- Lecturas ----------

def test_ultimas_lecturas_sin_datos(motor):
    estados = c.ultimas_lecturas(TECNICO, INVERNADERO)
    assert len(estados) == 4
    assert {e.status for e in estados} == {"no_data"}


def test_ultimas_lecturas_compara_con_umbral_y_optimo(motor):
    _guardar(
        motor,
        SensorData(sensor_id=SUELO_INVERNADERO, timestamp=AHORA - timedelta(hours=1), value=50),
        SensorData(sensor_id=SUELO_INVERNADERO, timestamp=AHORA, value=31.5),  # la más reciente
        SensorData(sensor_id=1, timestamp=AHORA, value=35),  # temperatura
        # Óptimo de prueba para el tomate del invernadero; no es un dato agronómico
        CropRange(crop_id=_cultivo(motor, "tomate"), type="temperature", optimal_min=15, optimal_max=30, source="test"),
    )
    estados = {e.sensor_id: e for e in c.ultimas_lecturas(AGRICULTOR, INVERNADERO)}
    suelo = estados[SUELO_INVERNADERO]
    assert (suelo.value, suelo.optimal_min, suelo.status) == (31.5, 40, "low")
    temperatura = estados[1]
    assert (temperatura.optimal_max, temperatura.status) == (30, "high")


def test_historico_filtra_por_fechas_y_ordena(motor):
    _guardar(motor, *[SensorData(sensor_id=1, timestamp=AHORA - timedelta(hours=h), value=h) for h in range(5)])
    datos = c.historico(AGRICULTOR, 1, AHORA - timedelta(hours=2), AHORA)
    assert [d.value for d in datos] == [2, 1, 0]
    assert len(c.historico(AGRICULTOR, 1, AHORA - timedelta(days=1), AHORA, limite=2)) == 2


def test_historico_con_parametros_malos(motor):
    with pytest.raises(ValueError):
        c.historico(AGRICULTOR, 1, AHORA, AHORA - timedelta(hours=1))
    with pytest.raises(ValueError):
        c.historico(AGRICULTOR, 1, AHORA - timedelta(hours=1), AHORA, limite=0)
    with pytest.raises(ValueError):
        c.historico(AGRICULTOR, 999, AHORA - timedelta(hours=1), AHORA)


# ---------- Cultivos y alertas ----------

def test_listar_cultivos(motor):
    aguacate = _cultivo(motor, "aguacate")
    _guardar(motor, CropRange(crop_id=aguacate, type="soil_moisture", optimal_min=30, optimal_max=60, source="test"))
    cultivos = {cu.name: cu for cu in c.listar_cultivos()}
    assert set(cultivos) == {"aguacate", "chirimoya", "mango", "tomate"}
    assert cultivos["aguacate"].ranges[0]["unit"] == "%"
    assert cultivos["mango"].ranges == []


def test_alertas_pendientes_y_marcar_leida(motor):
    _guardar(
        motor,
        Alert(sensor_id=SUELO_INVERNADERO, type="LOW", message="Suelo seco", timestamp=AHORA),
        Alert(sensor_id=5, type="HIGH", message="Calor", timestamp=AHORA + timedelta(minutes=1)),
    )
    assert [a.message for a in c.alertas_pendientes(TECNICO)] == ["Calor", "Suelo seco"]
    with pytest.raises(PermissionError):
        c.marcar_alerta_leida(TECNICO, 1)  # el técnico solo mira
    c.marcar_alerta_leida(AGRICULTOR, 1)
    assert [a.message for a in c.alertas_pendientes(AGRICULTOR)] == ["Calor"]
    assert c.alertas_pendientes(_otro_agricultor(motor)) == []


# ---------- Acciones ----------

def test_acciones_segun_tipo_de_parcela(motor):
    assert c.crear_accion(AGRICULTOR, INVERNADERO, "ventilation").status == "pending"
    assert c.crear_accion(AGRICULTOR, AGUACATES, "irrigation", 20).duration_min == 20
    with pytest.raises(ValueError, match="exterior"):
        c.crear_accion(AGRICULTOR, AGUACATES, "heating")  # en el campo no se calienta


def test_acciones_con_datos_o_permisos_malos(motor):
    with pytest.raises(ValueError):
        c.crear_accion(AGRICULTOR, INVERNADERO, "irrigation", 0)
    with pytest.raises(PermissionError):
        c.crear_accion(TECNICO, INVERNADERO, "irrigation")
    with pytest.raises(ValueError):
        c.crear_accion(AGRICULTOR, 999, "irrigation")


def test_los_objetos_se_pueden_usar_tras_cerrar_la_sesion(motor):
    parcela = c.listar_parcelas(AGRICULTOR)[0]
    assert isinstance(parcela, Parcel) and parcela.name  # no lanza DetachedInstanceError
