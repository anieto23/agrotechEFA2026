from datetime import datetime, timedelta, timezone

import pytest
from sqlmodel import Session, select

from agrotechEFA2026.db import consultas as c
from agrotechEFA2026.db.models import Alert, Crop, CropRange, Parcel, Sector, Sensor, SensorData, User
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


def _sector_nuevo() -> int:
    """Crea una parcela de prueba y devuelve el id de su único sector (sin sensores)."""
    parcela = c.crear_parcela(AGRICULTOR, "Huerto", "outdoor", 500, "rectangle")
    return c.listar_sectores(AGRICULTOR, parcela.id)[0].id


def test_crear_parcela_con_su_primer_sector(motor):
    p = c.crear_parcela(AGRICULTOR, "  Huerto  ", "indoor", 1200, "circle")
    assert (p.name, p.kind, p.area_m2, p.shape, p.owner_id) == ("Huerto", "indoor", 1200, "circle", AGRICULTOR)
    [sector] = c.listar_sectores(AGRICULTOR, p.id)
    assert (sector.name, sector.left_pct, sector.top_pct, sector.width_pct, sector.height_pct) == (
        "Sector 1", 0, 0, 100, 100)
    assert sector.crop_id is None  # «sin cultivo» hasta que se elija


@pytest.mark.parametrize(
    "nombre, tipo, area, forma",
    [
        ("", "outdoor", 10, "rectangle"),
        ("X" * 81, "outdoor", 10, "rectangle"),
        ("X", "garaje", 10, "rectangle"),  # ni interior ni exterior
        ("X", "indoor", 0, "rectangle"),
        ("X", "indoor", 1e12, "rectangle"),
        ("X", "indoor", 10, "triangulo"),
    ],
)
def test_crear_parcela_con_datos_malos(motor, nombre, tipo, area, forma):
    with pytest.raises(ValueError):
        c.crear_parcela(AGRICULTOR, nombre, tipo, area, forma)


CUADRADO = [[10, 10], [90, 10], [90, 90], [10, 90]]


def test_crear_parcela_dibujada_guarda_su_contorno(motor):
    p = c.crear_parcela(AGRICULTOR, "Bancal", "outdoor", 300, "drawn", CUADRADO)
    assert c.obtener_parcela(AGRICULTOR, p.id).outline == CUADRADO
    assert c.crear_parcela(AGRICULTOR, "Otra", "outdoor", 300, "square").outline is None


@pytest.mark.parametrize(
    "contorno, motivo",
    [
        (None, "tres vértices"),
        ([[0, 0], [50, 0]], "tres vértices"),
        ([[0, 0], [150, 0], [0, 50]], "dentro del plano"),
        ([[0, 0], [50, 0], [0, 0], [0, 50]], "repetir"),
        ([[0, 0], [50, 50], [100, 100]], "superficie"),
        ([[0, 0], [100, 100], [100, 0], [0, 60]], "cruzarse"),  # pajarita
        ([[0, 0], [50, 0], [50, 50], [25, 0], [0, 50]], "cruzarse"),  # un vértice toca otro lado
        ([["a", 0], [50, 0], [0, 50]], "par de números"),
        ([[0, 0, 0], [50, 0], [0, 50]], "par de números"),
    ],
)
def test_contorno_no_valido(motor, contorno, motivo):
    with pytest.raises(ValueError, match=motivo):
        c.crear_parcela(AGRICULTOR, "Bancal", "outdoor", 300, "drawn", contorno)


def test_contorno_solo_en_parcelas_dibujadas(motor):
    with pytest.raises(ValueError, match="dibujada"):
        c.crear_parcela(AGRICULTOR, "Bancal", "outdoor", 300, "square", CUADRADO)


def test_contorno_concavo_es_valido():
    # Forma de L: tiene un entrante, pero no se cruza
    contorno = [[0, 0], [60, 0], [60, 40], [30, 40], [30, 100], [0, 100]]
    assert c.validar_contorno(contorno) == contorno


def test_tecnico_no_crea_parcelas(motor):
    with pytest.raises(PermissionError):
        c.crear_parcela(TECNICO, "X", "indoor", 10, "square")


def test_eliminar_parcela_borra_todo_lo_suyo(motor):
    _guardar(
        motor,
        SensorData(sensor_id=SUELO_INVERNADERO, timestamp=AHORA, value=30),
        Alert(sensor_id=SUELO_INVERNADERO, type="LOW", message="Seco", timestamp=AHORA),
    )
    c.crear_accion(AGRICULTOR, INVERNADERO, "irrigation", 10)
    c.eliminar_parcela(AGRICULTOR, INVERNADERO)
    assert c.obtener_parcela(AGRICULTOR, INVERNADERO) is None
    with Session(motor) as s:
        assert s.exec(select(Sector).where(Sector.parcel_id == INVERNADERO)).all() == []
        assert s.get(Sensor, SUELO_INVERNADERO) is None
        assert s.exec(select(SensorData)).all() == []
        assert s.exec(select(Alert)).all() == []
    assert len(c.listar_parcelas(AGRICULTOR)) == 2  # las otras siguen ahí


def test_solo_el_dueno_elimina(motor):
    with pytest.raises(PermissionError):
        c.eliminar_parcela(TECNICO, INVERNADERO)
    with pytest.raises(ValueError):
        c.eliminar_parcela(AGRICULTOR, 999)


# ---------- Sectores y sensores ----------

def test_dividir_sector_en_vertical_y_horizontal(motor):
    sector_id = _sector_nuevo()
    c.cambiar_cultivo(AGRICULTOR, sector_id, _cultivo(motor, "tomate"))
    izquierda, derecha = c.dividir_sector(AGRICULTOR, sector_id, "vertical")
    assert (izquierda.left_pct, izquierda.width_pct) == (0, 50)
    assert (derecha.left_pct, derecha.width_pct, derecha.height_pct) == (50, 50, 100)
    assert derecha.name == "Sector 2" and derecha.crop_id == izquierda.crop_id  # conserva el cultivo
    arriba, abajo = c.dividir_sector(AGRICULTOR, derecha.id, "horizontal")
    assert (abajo.left_pct, abajo.top_pct, abajo.width_pct, abajo.height_pct) == (50, 50, 50, 50)
    assert arriba.height_pct == 50 and abajo.name == "Sector 3"


def test_dividir_sector_con_datos_malos(motor):
    sector_id = _sector_nuevo()
    with pytest.raises(ValueError):
        c.dividir_sector(AGRICULTOR, sector_id, "diagonal")
    with pytest.raises(ValueError, match="pequeño"):
        for _ in range(10):  # 100 → 50 → 25 → ... hasta menos del 2 %
            c.dividir_sector(AGRICULTOR, sector_id, "vertical")
    with pytest.raises(PermissionError):
        c.dividir_sector(TECNICO, sector_id, "vertical")


def test_cambiar_cultivo(motor):
    sector_id = _sector_nuevo()
    assert c.cambiar_cultivo(AGRICULTOR, sector_id, _cultivo(motor, "mango")).crop_id == _cultivo(motor, "mango")
    assert c.cambiar_cultivo(AGRICULTOR, sector_id, None).crop_id is None
    with pytest.raises(ValueError, match="cultivo"):
        c.cambiar_cultivo(AGRICULTOR, sector_id, 999)


def test_crear_sensor_y_validar_umbrales(motor):
    sector_id = _sector_nuevo()
    sensor = c.crear_sensor(AGRICULTOR, sector_id, "temperature", 15, 30)
    assert (sensor.unit, sensor.threshold_low) == ("ºC", 15)
    with pytest.raises(ValueError, match="ya tiene"):
        c.crear_sensor(AGRICULTOR, sector_id, "temperature")  # uno de cada tipo por sector
    with pytest.raises(ValueError):
        c.crear_sensor(AGRICULTOR, sector_id, "ph")
    with pytest.raises(ValueError):
        c.crear_sensor(AGRICULTOR, sector_id, "air_humidity", 80, 20)  # bajo mayor que alto
    with pytest.raises(ValueError):
        c.crear_sensor(AGRICULTOR, sector_id, "soil_moisture", None, 150)  # fuera de 0-100 %
    with pytest.raises(PermissionError):
        c.crear_sensor(TECNICO, sector_id, "light")


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
